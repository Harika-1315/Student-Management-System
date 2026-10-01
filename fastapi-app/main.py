# ---------------- SUMMARY ----------------

@app.post("/materials/{material_id}/summary")
def get_summary(
    material_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    material = db.query(Material).filter(
        Material.id == material_id,
        Material.owner_id == current_user.id
    ).first()

    if not material:
        raise HTTPException(
            status_code=404,
            detail="Material not found"
        )

    text = material.content.strip()

    if not text:
        raise HTTPException(
            status_code=400,
            detail="No text available for summary"
        )

    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    summary = " ".join(sentences[:5])

    return {
        "material_id": material.id,
        "summary": summary
    }


# ---------------- QUIZ ----------------

@app.post("/materials/{material_id}/quiz")
def generate_quiz(
    material_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    material = db.query(Material).filter(
        Material.id == material_id,
        Material.owner_id == current_user.id
    ).first()

    if not material:
        raise HTTPException(
            status_code=404,
            detail="Material not found"
        )

    text = material.content.strip()

    if not text:
        raise HTTPException(
            status_code=400,
            detail="No text available for quiz generation"
        )

    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if len(s.strip().split()) >= 5]

    quiz = []

    for index, sentence in enumerate(sentences[:5], start=1):
        words = sentence.split()

        if len(words) >= 5:
            answer = words[0].strip(".,!?")
            question = sentence.replace(words[0], "_____", 1)

            quiz.append({
                "question_number": index,
                "question": question,
                "answer": answer
            })

    return {
        "material_id": material.id,
        "quiz": quiz
    }
