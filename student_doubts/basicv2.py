import tkinter as tk
from tkinter import ttk, messagebox

# ── credentials ──
USERS = {
    "student1": {"password": "s123", "role": "student"},
    "teacher1": {"password": "t123", "role": "teacher"},
}

# ── shared doubts store ──
doubts = []
_id = [1]


# ═════════════════════════════
# LOGIN
# ═════════════════════════════
def show_login(root):
    clear(root)

    tk.Label(root, text="Login").pack()

    tk.Label(root, text="Username").pack()
    user_e = tk.Entry(root)
    user_e.pack()

    tk.Label(root, text="Password").pack()
    pass_e = tk.Entry(root, show="*")
    pass_e.pack()

    def login():
        u = user_e.get()
        p = pass_e.get()

        if u in USERS and USERS[u]["password"] == p:
            if USERS[u]["role"] == "student":
                show_student(root, u)
            else:
                show_teacher(root, u)
        else:
            messagebox.showerror("Error", "Invalid login")

    tk.Button(root, text="Login", command=login).pack()


# ═════════════════════════════
# COMMON HEADER
# ═════════════════════════════
def header(root, title):
    tk.Label(root, text=title).pack()
    tk.Button(root, text="Logout", command=lambda: show_login(root)).pack(anchor="ne")


# ═════════════════════════════
# STUDENT DASHBOARD
# ═════════════════════════════
def show_student(root, username):
    clear(root)

    header(root, f"Student: {username}")

    # Subject (Combobox)
    tk.Label(root, text="Subject").pack()
    subj_combo = ttk.Combobox(root, values=["Math", "Science", "English"], state="readonly")
    subj_combo.pack()
    subj_combo.set("Select Subject")

    # Teacher (Combobox)
    tk.Label(root, text="Teacher").pack()
    teacher_combo = ttk.Combobox(root, values=["Mr. Sharma", "Ms. Roy", "Dr. Sen"], state="readonly")
    teacher_combo.pack()
    teacher_combo.set("Select Teacher")

    # Severity (Radio Buttons)
    tk.Label(root, text="Severity").pack()
    severity = tk.StringVar()

    tk.Radiobutton(root, text="Low", variable=severity, value="Low").pack()
    tk.Radiobutton(root, text="Medium", variable=severity, value="Medium").pack()
    tk.Radiobutton(root, text="High", variable=severity, value="High").pack()

    # Extra options (Checkbuttons)
    tk.Label(root, text="Options").pack()
    urgent_var = tk.IntVar()
    explain_var = tk.IntVar()

    tk.Checkbutton(root, text="Urgent", variable=urgent_var).pack()
    tk.Checkbutton(root, text="Need Explanation", variable=explain_var).pack()

    # Description
    tk.Label(root, text="Description").pack()
    desc_t = tk.Text(root, height=3)
    desc_t.pack()

    def submit():
        s = subj_combo.get()
        t = teacher_combo.get()
        sev = severity.get()
        d = desc_t.get("1.0", "end").strip()

        urgent = "Yes" if urgent_var.get() == 1 else "No"
        explain = "Yes" if explain_var.get() == 1 else "No"

        if s == "Select Subject" or t == "Select Teacher" or not d or not sev:
            messagebox.showwarning("Warning", "Fill all fields")
            return

        doubts.append({
            "id": _id[0],
            "student": username,
            "subject": s,
            "teacher": t,
            "severity": sev,
            "urgent": urgent,
            "explain": explain,
            "desc": d,
            "reply": ""
        })

        _id[0] += 1

        # Clear inputs
        subj_combo.set("Select Subject")
        teacher_combo.set("Select Teacher")
        severity.set("")
        urgent_var.set(0)
        explain_var.set(0)
        desc_t.delete("1.0", "end")

        refresh_list()

    tk.Button(root, text="Submit", command=submit).pack()

    # Table
    cols = ("ID", "Subject", "Teacher", "Severity", "Description", "Reply")
    tree = ttk.Treeview(root, columns=cols, show="headings")

    for c in cols:
        tree.heading(c, text=c)

    tree.pack()

    def refresh_list():
        tree.delete(*tree.get_children())

        for d in doubts:
            if d["student"] == username:
                tree.insert("", "end", values=(
                    d["id"],
                    d["subject"],
                    d.get("teacher", ""),
                    d.get("severity", ""),
                    d["desc"],
                    d["reply"] or "Pending"
                ))

    refresh_list()


# ═════════════════════════════
# TEACHER DASHBOARD
# ═════════════════════════════
def show_teacher(root, username):
    clear(root)

    header(root, f"Teacher: {username}")

    cols = ("ID", "Student", "Subject", "Teacher", "Severity", "Description", "Reply")
    tree = ttk.Treeview(root, columns=cols, show="headings")

    for c in cols:
        tree.heading(c, text=c)

    tree.pack()

    def load():
        tree.delete(*tree.get_children())

        for d in doubts:
            tree.insert("", "end", iid=str(d["id"]), values=(
                d["id"],
                d["student"],
                d["subject"],
                d.get("teacher", ""),
                d.get("severity", ""),
                d["desc"],
                d["reply"]
            ))

    load()

    tk.Label(root, text="Reply").pack()
    reply_e = tk.Entry(root)
    reply_e.pack()

    def send_reply():
        sel = tree.selection()

        if not sel:
            messagebox.showwarning("Warning", "Select a doubt")
            return

        did = int(sel[0])
        txt = reply_e.get()

        if not txt:
            messagebox.showwarning("Warning", "Write reply")
            return

        for d in doubts:
            if d["id"] == did:
                d["reply"] = txt
                break

        reply_e.delete(0, "end")
        load()

    tk.Button(root, text="Send Reply", command=send_reply).pack()


# ═════════════════════════════
# HELPERS
# ═════════════════════════════
def clear(root):
    for w in root.winfo_children():
        w.destroy()


# ═════════════════════════════
# MAIN
# ═════════════════════════════
root = tk.Tk()
root.title("Doubt Management System")
root.geometry("500x500")

show_login(root)
root.mainloop()