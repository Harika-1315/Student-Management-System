from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
import os
import fitz
import pytesseract
from PIL import Image
import io
import re

app = FastAPI(title="Saralvidhya Study Materials API")

# ---------------- DATABASE ----------------

DATABASE_URL = "sqlite:///./materials.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    content = Column(Text)
    owner_id = Column(Integer)


Base.metadata.create_all(bind=engine)

# ---------------- AUTHENTICATION ----------------

SECRET_KEY = os.getenv("JWT_SECRET", "change-this-secret")
ALGORITHM = "HS256"

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)

security = HTTPBearer()


class UserCreate(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_token(user_id: int):
    payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(hours=2)
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = int(payload["sub"])

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user


# ---------------- USER REGISTRATION ----------------

@app.post("/users")
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(User).filter(
        User.username == user.username
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    new_user = User(
        username=user.username,
        password_hash=pwd_context.hash(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User created successfully",
        "user_id": new_user.id
    }


# ---------------- LOGIN ----------------

@app.post("/auth/login")
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.username == credentials.username
    ).first()

    if not user or not pwd_context.verify(
        credentials.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    token = create_token(user.id)

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# ---------------- PDF TEXT / OCR ----------------

def extract_pdf_text(pdf_bytes: bytes):

    document = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    pages = []

    for page in document:

        text = page.get_text()

        # If page has little/no text, use OCR
        if len(text.strip()) < 30:
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            image = Image.open(
                io.BytesIO(pix.tobytes("png"))
            )

            text = pytesseract.image_to_string(image)

        pages.append(text)

    return "\n".join(pages)


# ---------------- PDF UPLOAD ----------------

@app.post("/materials/upload")
async def upload_material(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    pdf_bytes = await file.read()

    try:
        text = extract_pdf_text(pdf_bytes)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PDF/OCR processing failed: {str(e)}"
        )

    material = Material(
        filename=file.filename,
        content=text,
        owner_id=current_user.id
    )

    db.add(material)
    db.commit()
    db.refresh(material)

    return {
        "message": "PDF uploaded successfully",
        "material_id": material.id,
        "characters_extracted": len(text)
    }


# ---------------- AUTHORIZATION CHECK ----------------

def get_material(
    material_id: int,
    current_user: User,
    db: Session
):

    material = db.query(Material).filter(
        Material.id == material_id
    ).first()

    if not material:
        raise HTTPException(
            status_code=404,
            detail="Material not found"
        )

    if material.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    return material


# ---------------- SUMMARY ----------------

@app.post("/materials/{material_id}/summary")
def generate_summary(
    material_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    material = get_material(
        material_id,
        current_user,
        db
    )

    text = material.content.strip()

    if not text:
        return {
            "material_id": material_id,
            "summary": "No readable text was found in the PDF."
        }

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text
    )

    summary = " ".join(sentences[:5])

    return {
        "material_id": material_id,
        "summary": summary
    }


# ---------------- QUIZ ----------------

@app.post("/materials/{material_id}/quiz")
def generate_quiz(
    material_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    material = get_material(
        material_id,
        current_user,
        db
    )

    text = material.content.strip()

    if not text:
        return {
            "material_id": material_id,
            "quiz": []
        }

    sentences = [
        s.strip()
        for s in re.split(r"(?<=[.!?])\s+", text)
        if len(s.strip()) > 40
    ]

    quiz = []

    for index, sentence in enumerate(sentences[:5], start=1):

        words = sentence.split()

        if len(words) > 6:
            answer = words[-1].strip(".,!?")
            question = sentence.replace(
                answer,
                "_____",
                1
            )

            quiz.append({
                "question": f"What completes this statement: {question}",
                "answer": answer
            })

    return {
        "material_id": material_id,
        "quiz": quiz
    }


# ---------------- HEALTH CHECK ----------------

@app.get("/")
def root():
    return {
        "message": "Saralvidhya Study Materials API is running"
    }
