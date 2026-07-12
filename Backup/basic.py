# import tkinter as tk
# from tkinter import ttk, messagebox

# # ── credentials ──────────────────────────────────────────────
# USERS = {
#     "student1": {"password": "s123", "role": "student"},
#     "teacher1": {"password": "t123", "role": "teacher"},
# }

# # ── shared doubts store ───────────────────────────────────────
# doubts = []   # [{"id":1, "student":"", "subject":"", "desc":"", "reply":""}]
# _id = [1]


# # ══════════════════════════════════════════════════════════════
# #  LOGIN
# # ══════════════════════════════════════════════════════════════
# def show_login(root):
#     clear(root)
#     root.title("Student Doubt Logger – Login")
#     root.geometry("420x340")

#     frm = tk.Frame(root, bg="#d0d0d0", bd=0)
#     frm.place(relx=.5, rely=.5, anchor="center", width=300, height=260)

#     tk.Label(frm, text="Login", font=("Helvetica", 18, "bold"), bg="#d0d0d0").pack(pady=(20, 2))
#     tk.Label(frm, text="Please login to continue", font=("Helvetica", 9), bg="#d0d0d0", fg="#555").pack()

#     tk.Label(frm, text="Username", bg="#d0d0d0", anchor="w").pack(fill="x", padx=30, pady=(14, 0))
#     user_e = tk.Entry(frm, font=("Helvetica", 10)); user_e.pack(padx=30, fill="x", ipady=4)
#     user_e.insert(0, "Type here...")
#     user_e.bind("<FocusIn>", lambda e: user_e.delete(0, "end") if user_e.get() == "Type here..." else None)

#     tk.Label(frm, text="Password", bg="#d0d0d0", anchor="w").pack(fill="x", padx=30, pady=(8, 0))
#     pass_e = tk.Entry(frm, font=("Helvetica", 10), show="*"); pass_e.pack(padx=30, fill="x", ipady=4)

#     def login():
#         u, p = user_e.get().strip(), pass_e.get().strip()
#         if u in USERS and USERS[u]["password"] == p:
#             if USERS[u]["role"] == "student":
#                 show_student(root, u)
#             else:
#                 show_teacher(root, u)
#         else:
#             messagebox.showerror("Login Failed", "Invalid username or password.")

#     tk.Button(frm, text="Login", bg="#5b8dee", fg="white", font=("Helvetica", 10, "bold"),
#               relief="flat", cursor="hand2", command=login).pack(pady=14, ipadx=20, ipady=4)


# # ══════════════════════════════════════════════════════════════
# #  STUDENT DASHBOARD
# # ══════════════════════════════════════════════════════════════
# def show_student(root, username):
#     clear(root)
#     root.title(f"Student Dashboard – {username}")
#     root.geometry("600x500")

#     header(root, f"Student Dashboard  ·  {username}", lambda: show_login(root))

#     frm = tk.Frame(root, bg="#f4f6fb"); frm.pack(fill="both", expand=True, padx=20, pady=10)

#     # ── submit doubt ──
#     box = labeled_box(frm, "Submit a Doubt")

#     tk.Label(box, text="Subject", bg="white", anchor="w").pack(fill="x", pady=(4,0))
#     subj_e = tk.Entry(box, font=("Helvetica", 10)); subj_e.pack(fill="x", ipady=3)

#     tk.Label(box, text="Description", bg="white", anchor="w").pack(fill="x", pady=(6,0))
#     desc_t = tk.Text(box, height=3, font=("Helvetica", 10), wrap="word"); desc_t.pack(fill="x")

#     def submit():
#         s, d = subj_e.get().strip(), desc_t.get("1.0", "end").strip()
#         if not s or not d:
#             messagebox.showwarning("Empty", "Fill subject & description."); return
#         doubts.append({"id": _id[0], "student": username, "subject": s, "desc": d, "reply": ""})
#         _id[0] += 1
#         subj_e.delete(0, "end"); desc_t.delete("1.0", "end")
#         refresh_list()
#         messagebox.showinfo("Submitted", "Doubt submitted!")

#     tk.Button(box, text="Submit Doubt", bg="#5b8dee", fg="white", relief="flat",
#               cursor="hand2", command=submit).pack(pady=6, anchor="w", ipadx=10, ipady=3)

#     # ── my doubts ──
#     box2 = labeled_box(frm, "My Doubts & Replies")
#     cols = ("ID", "Subject", "Description", "Reply")
#     tree = ttk.Treeview(box2, columns=cols, show="headings", height=6)
#     for c in cols: tree.heading(c, text=c); tree.column(c, width=130 if c != "ID" else 30)
#     tree.pack(fill="both", expand=True)
#     sb = ttk.Scrollbar(box2, orient="vertical", command=tree.yview)
#     tree.configure(yscrollcommand=sb.set); sb.pack(side="right", fill="y")

#     def refresh_list():
#         tree.delete(*tree.get_children())
#         for d in doubts:
#             if d["student"] == username:
#                 tree.insert("", "end", values=(d["id"], d["subject"], d["desc"][:40], d["reply"] or "Pending"))

#     refresh_list()


# # ══════════════════════════════════════════════════════════════
# #  TEACHER DASHBOARD
# # ══════════════════════════════════════════════════════════════
# def show_teacher(root, username):
#     clear(root)
#     root.title(f"Teacher Dashboard – {username}")
#     root.geometry("700x520")

#     header(root, f"Teacher Dashboard  ·  {username}", lambda: show_login(root))

#     frm = tk.Frame(root, bg="#f4f6fb"); frm.pack(fill="both", expand=True, padx=20, pady=10)
#     box = labeled_box(frm, "All Student Doubts")

#     cols = ("ID", "Student", "Subject", "Description", "Reply")
#     tree = ttk.Treeview(box, columns=cols, show="headings", height=10)
#     widths = {"ID": 30, "Student": 80, "Subject": 110, "Description": 200, "Reply": 150}
#     for c in cols: tree.heading(c, text=c); tree.column(c, width=widths[c])
#     tree.pack(fill="both", expand=True)

#     def load():
#         tree.delete(*tree.get_children())
#         for d in doubts:
#             tree.insert("", "end", iid=str(d["id"]),
#                         values=(d["id"], d["student"], d["subject"], d["desc"][:50], d["reply"] or "—"))

#     load()

#     # reply area
#     rfrm = tk.Frame(frm, bg="#f4f6fb"); rfrm.pack(fill="x", pady=8)
#     tk.Label(rfrm, text="Reply to selected doubt:", bg="#f4f6fb").pack(anchor="w")
#     reply_e = tk.Entry(rfrm, font=("Helvetica", 10)); reply_e.pack(fill="x", ipady=4)

#     def send_reply():
#         sel = tree.selection()
#         if not sel: messagebox.showwarning("Select", "Select a doubt first."); return
#         did = int(sel[0]); txt = reply_e.get().strip()
#         if not txt: messagebox.showwarning("Empty", "Write a reply."); return
#         for d in doubts:
#             if d["id"] == did: d["reply"] = txt; break
#         reply_e.delete(0, "end"); load()
#         messagebox.showinfo("Sent", "Reply saved!")

#     tk.Button(rfrm, text="Send Reply", bg="#27ae60", fg="white", relief="flat",
#               cursor="hand2", command=send_reply).pack(pady=4, anchor="w", ipadx=10, ipady=3)


# # ══════════════════════════════════════════════════════════════
# #  HELPERS
# # ══════════════════════════════════════════════════════════════
# def clear(root):
#     for w in root.winfo_children(): w.destroy()

# def header(root, title, logout_cmd):
#     bar = tk.Frame(root, bg="#1a1a2e", height=40)
#     bar.pack(fill="x"); bar.pack_propagate(False)
#     tk.Label(bar, text=title, bg="#1a1a2e", fg="white",
#              font=("Helvetica", 11, "bold")).pack(side="left", padx=12)
#     tk.Button(bar, text="Logout", bg="#e74c3c", fg="white", relief="flat",
#               cursor="hand2", command=logout_cmd).pack(side="right", padx=10, pady=5)

# def labeled_box(parent, title):
#     lf = tk.LabelFrame(parent, text=title, bg="white", font=("Helvetica", 9, "bold"),
#                         padx=8, pady=6)
#     lf.pack(fill="both", expand=True, pady=6)
#     return lf


# # ══════════════════════════════════════════════════════════════
# if __name__ == "__main__":
#     root = tk.Tk()
#     root.configure(bg="#e8e8e8")
#     show_login(root)
#     root.mainloop()
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

    # Subject
    tk.Label(root, text="Subject").pack()
    subj_e = tk.Entry(root)
    subj_e.pack()

    # Description
    tk.Label(root, text="Description").pack()
    desc_t = tk.Text(root, height=3)
    desc_t.pack()

    def submit():
        s = subj_e.get()
        d = desc_t.get("1.0", "end").strip()

        if not s or not d:
            messagebox.showwarning("Warning", "Fill all fields")
            return

        doubts.append({
            "id": _id[0],
            "student": username,
            "subject": s,
            "desc": d,
            "reply": ""
        })

        _id[0] += 1

        subj_e.delete(0, "end")
        desc_t.delete("1.0", "end")

        refresh_list()

    tk.Button(root, text="Submit", command=submit).pack()

    # Table
    cols = ("ID", "Subject", "Description", "Reply")
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

    cols = ("ID", "Student", "Subject", "Description", "Reply")
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
show_login(root)
root.mainloop()