from tkinter import *
from tkinter import ttk

student_id = 1000

# ---------------- FUNCTIONS ---------------- #

def add_student():
    global student_id

    name = name_entry.get().strip()
    dept = dept_var.get()
    phone = phone_entry.get().strip()
    email = email_entry.get().strip()

    if name == "":
        return

    student_id += 1

    table.insert(
        "",
        END,
        values=(student_id, name, dept, phone, email)
    )

    name_entry.delete(0, END)
    phone_entry.delete(0, END)
    email_entry.delete(0, END)


def delete_student():
    selected = table.selection()

    if selected:
        table.delete(selected[0])


def search_student():
    search_text = search_entry.get().lower()

    for item in table.get_children():

        values = table.item(item)["values"]

        data = " ".join(map(str, values)).lower()

        if search_text in data:
            table.selection_set(item)
            table.focus(item)
            table.see(item)
            break


def save_students():

    with open("students.txt", "w") as file:

        for item in table.get_children():

            values = table.item(item)["values"]

            file.write("|".join(map(str, values)) + "\n")


def load_students():
    global student_id

    try:

        with open("students.txt", "r") as file:

            for line in file:

                data = line.strip().split("|")

                if len(data) == 5:

                    table.insert(
                        "",
                        END,
                        values=data
                    )

                    sid = int(data[0])

                    if sid > student_id:
                        student_id = sid

    except:
        pass


# ---------------- WINDOW ---------------- #

root = Tk()

root.title("Student Management System")
root.geometry("1050x750")
root.configure(bg="#0B132B")
root.resizable(False, False)

# ---------------- COLORS ---------------- #

BG = "#0B132B"
CARD = "#1C2541"
TEXT = "white"
PRIMARY = "#3A86FF"
SUCCESS = "#06D6A0"
DANGER = "#EF476F"
INPUT = "#3A506B"

# ---------------- TITLE ---------------- #

title = Label(
    root,
    text="Student Management System",
    font=("Segoe UI", 28, "bold"),
    bg=BG,
    fg=TEXT
)

title.pack(pady=20)

# ---------------- CARD ---------------- #

main_frame = Frame(
    root,
    bg=CARD,
    padx=25,
    pady=25
)

main_frame.pack(pady=10)

# ---------------- NAME ---------------- #

Label(
    main_frame,
    text="Student Name",
    bg=CARD,
    fg="white",
    font=("Segoe UI", 10)
).pack(anchor="w")

name_entry = Entry(
    main_frame,
    width=35,
    font=("Segoe UI", 11),
    bg=INPUT,
    fg="white",
    insertbackground="white",
    relief=FLAT
)

name_entry.pack(pady=5, ipady=5)

# ---------------- DEPARTMENT ---------------- #

Label(
    main_frame,
    text="Department",
    bg=CARD,
    fg="white",
    font=("Segoe UI", 10)
).pack(anchor="w")

dept_var = StringVar()
dept_var.set("CSE")

dept_menu = ttk.Combobox(
    main_frame,
    textvariable=dept_var,
    values=["CSE", "AIML", "ECE", "EEE", "MECH"],
    state="readonly",
    width=32
)

dept_menu.pack(pady=5)

# ---------------- PHONE ---------------- #

Label(
    main_frame,
    text="Phone Number",
    bg=CARD,
    fg="white",
    font=("Segoe UI", 10)
).pack(anchor="w")

phone_entry = Entry(
    main_frame,
    width=35,
    font=("Segoe UI", 11),
    bg=INPUT,
    fg="white",
    insertbackground="white",
    relief=FLAT
)

phone_entry.pack(pady=5, ipady=5)

# ---------------- EMAIL ---------------- #

Label(
    main_frame,
    text="Email Address",
    bg=CARD,
    fg="white",
    font=("Segoe UI", 10)
).pack(anchor="w")

email_entry = Entry(
    main_frame,
    width=35,
    font=("Segoe UI", 11),
    bg=INPUT,
    fg="white",
    insertbackground="white",
    relief=FLAT
)

email_entry.pack(pady=5, ipady=5)

# ---------------- BUTTONS ---------------- #

btn_frame = Frame(main_frame, bg=CARD)
btn_frame.pack(pady=15)

Button(
    btn_frame,
    text="Add Student",
    bg=PRIMARY,
    fg="white",
    relief=FLAT,
    width=15,
    command=add_student
).grid(row=0, column=0, padx=10)

Button(
    btn_frame,
    text="Delete Student",
    bg=DANGER,
    fg="white",
    relief=FLAT,
    width=15,
    command=delete_student
).grid(row=0, column=1, padx=10)

# ---------------- SEARCH ---------------- #

search_entry = Entry(
    main_frame,
    width=35,
    font=("Segoe UI", 11)
)

search_entry.pack(pady=10)

search_frame = Frame(main_frame, bg=CARD)
search_frame.pack()

Button(
    search_frame,
    text="Search",
    bg="#F4A261",
    fg="white",
    relief=FLAT,
    width=12,
    command=search_student
).grid(row=0, column=0, padx=10)

Button(
    search_frame,
    text="Save",
    bg=SUCCESS,
    fg="white",
    relief=FLAT,
    width=12,
    command=save_students
).grid(row=0, column=1, padx=10)

# ---------------- TABLE ---------------- #

style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Treeview",
    background="#111827",
    foreground="white",
    fieldbackground="#111827",
    rowheight=28
)

style.configure(
    "Treeview.Heading",
    font=("Segoe UI", 10, "bold")
)

table_frame = Frame(root)
table_frame.pack(pady=20)

scroll = Scrollbar(table_frame)
scroll.pack(side=RIGHT, fill=Y)

table = ttk.Treeview(
    table_frame,
    yscrollcommand=scroll.set,
    columns=("ID", "Name", "Dept", "Phone", "Email"),
    show="headings",
    height=12
)

table.heading("ID", text="ID")
table.heading("Name", text="Name")
table.heading("Dept", text="Department")
table.heading("Phone", text="Phone")
table.heading("Email", text="Email")

table.column("ID", width=80)
table.column("Name", width=180)
table.column("Dept", width=120)
table.column("Phone", width=150)
table.column("Email", width=250)

table.pack()

scroll.config(command=table.yview)

# ---------------- FOOTER ---------------- #

footer = Label(
    root,
    text="Developed by Yasmin Shaik",
    bg=BG,
    fg="#A0AEC0",
    font=("Segoe UI", 10)
)

footer.pack(pady=10)

# ---------------- LOAD DATA ---------------- #

load_students()

root.mainloop()