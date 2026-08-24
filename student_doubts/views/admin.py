import tkinter as tk
from tkinter import ttk, messagebox

from . import style


class AdminDashboardFrame(tk.Frame):
    """Administration workspace for people, academic categories, and doubts."""

    STATUSES = ("Pending", "Assigned", "Replied", "Resolved")
    ROLES = ("student", "teacher", "admin")

    def __init__(self, parent, store, username):
        super().__init__(parent, bg=style.BG_MAIN)
        self.store = store
        self.username = username
        self.selected_doubt_id = None
        self._build()
        self.refresh_all()

    def _build(self):
        outer = tk.Frame(self, bg=style.BG_MAIN)
        outer.pack(fill="both", expand=True, padx=16, pady=14)

        self.metrics = tk.Frame(outer, bg=style.BG_MAIN)
        self.metrics.pack(fill="x", pady=(0, 12))
        self.metric_vars = {key: tk.StringVar(value="—") for key in ("active_users", "total_doubts", "open_doubts", "top_subject")}
        labels = (("Active users", "active_users"), ("All doubts", "total_doubts"), ("Needs attention", "open_doubts"), ("Most requested subject", "top_subject"))
        for title, key in labels:
            card = tk.Frame(self.metrics, bg=style.BG_CARD, bd=1, relief="solid")
            card.pack(side="left", fill="x", expand=True, padx=4)
            tk.Label(card, text=title, font=style.FONT_LABEL, bg=style.BG_CARD, fg=style.FG_MUTED).pack(anchor="w", padx=12, pady=(8, 0))
            tk.Label(card, textvariable=self.metric_vars[key], font=style.FONT_HEADING, bg=style.BG_CARD, fg=style.FG_DARK).pack(anchor="w", padx=12, pady=(0, 8))

        notebook = ttk.Notebook(outer)
        notebook.pack(fill="both", expand=True)
        self._build_doubts_tab(notebook)
        self._build_users_tab(notebook)
        self._build_subjects_tab(notebook)

    def _tree(self, parent, columns, widths):
        holder = tk.Frame(parent, bg=style.BG_CARD)
        tree = ttk.Treeview(holder, columns=columns, show="headings")
        scroll = ttk.Scrollbar(holder, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        for col in columns:
            tree.heading(col, text=col, anchor="w")
            tree.column(col, width=widths.get(col, 100), minwidth=55, stretch=True)
        scroll.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)
        return holder, tree

    def _build_doubts_tab(self, notebook):
        tab = tk.Frame(notebook, bg=style.BG_CARD, padx=12, pady=12)
        notebook.add(tab, text="Doubt oversight")
        table, self.doubt_tree = self._tree(tab, ("ID", "Student", "Subject", "Assigned to", "Severity", "Points", "Status"), {"ID": 48, "Student": 110, "Subject": 120, "Assigned to": 120, "Severity": 85, "Points": 70, "Status": 95})
        table.pack(side="left", fill="both", expand=True, padx=(0, 12))
        self.doubt_tree.bind("<<TreeviewSelect>>", self._on_doubt_selected)

        actions = tk.LabelFrame(tab, text="Selected doubt", font=style.FONT_TITLE, bg=style.BG_CARD, fg=style.FG_DARK, padx=10, pady=10, width=245)
        actions.pack(side="right", fill="y")
        actions.pack_propagate(False)
        self.doubt_detail = tk.StringVar(value="Choose a doubt to manage its assignment or status.")
        tk.Label(actions, textvariable=self.doubt_detail, wraplength=210, justify="left", font=style.FONT_BODY, bg=style.BG_CARD, fg=style.FG_MUTED).pack(anchor="w", pady=(0, 12))
        tk.Label(actions, text="Assign resolver", font=style.FONT_LABEL, bg=style.BG_CARD, fg=style.FG_MUTED).pack(anchor="w")
        self.teacher_var = tk.StringVar()
        self.teacher_combo = ttk.Combobox(actions, textvariable=self.teacher_var, state="readonly")
        self.teacher_combo.pack(fill="x", pady=(2, 8))
        self._button(actions, "Assign / reassign", self.assign_selected).pack(fill="x", pady=(0, 12))
        tk.Label(actions, text="Set status", font=style.FONT_LABEL, bg=style.BG_CARD, fg=style.FG_MUTED).pack(anchor="w")
        self.status_var = tk.StringVar(value="Pending")
        ttk.Combobox(actions, textvariable=self.status_var, values=self.STATUSES, state="readonly").pack(fill="x", pady=(2, 8))
        self._button(actions, "Update status", self.update_status, success=True).pack(fill="x")

    def _build_users_tab(self, notebook):
        tab = tk.Frame(notebook, bg=style.BG_CARD, padx=12, pady=12)
        notebook.add(tab, text="Users & roles")
        table, self.user_tree = self._tree(tab, ("Username", "Role", "Account status"), {"Username": 190, "Role": 120, "Account status": 130})
        table.pack(side="left", fill="both", expand=True, padx=(0, 12))
        self.user_tree.bind("<<TreeviewSelect>>", self._on_user_selected)
        actions = tk.LabelFrame(tab, text="Account controls", font=style.FONT_TITLE, bg=style.BG_CARD, fg=style.FG_DARK, padx=10, pady=10, width=245)
        actions.pack(side="right", fill="y")
        actions.pack_propagate(False)
        self.user_detail = tk.StringVar(value="Choose an account to change its role or access.")
        tk.Label(actions, textvariable=self.user_detail, wraplength=210, justify="left", font=style.FONT_BODY, bg=style.BG_CARD, fg=style.FG_MUTED).pack(anchor="w", pady=(0, 12))
        tk.Label(actions, text="Role", font=style.FONT_LABEL, bg=style.BG_CARD, fg=style.FG_MUTED).pack(anchor="w")
        self.role_var = tk.StringVar(value="student")
        ttk.Combobox(actions, textvariable=self.role_var, values=self.ROLES, state="readonly").pack(fill="x", pady=(2, 8))
        self._button(actions, "Save role", self.update_role).pack(fill="x", pady=(0, 12))
        self.access_btn = self._button(actions, "Deactivate account", self.toggle_access, danger=True)
        self.access_btn.pack(fill="x")

    def _build_subjects_tab(self, notebook):
        tab = tk.Frame(notebook, bg=style.BG_CARD, padx=14, pady=14)
        notebook.add(tab, text="Subjects")
        tk.Label(tab, text="Academic categories", font=style.FONT_TITLE, bg=style.BG_CARD, fg=style.FG_DARK).pack(anchor="w")
        tk.Label(tab, text="Subjects keep doubt reporting and assignment organised.", font=style.FONT_BODY, bg=style.BG_CARD, fg=style.FG_MUTED).pack(anchor="w", pady=(2, 12))
        content = tk.Frame(tab, bg=style.BG_CARD)
        content.pack(fill="both", expand=True)
        self.subject_list = tk.Listbox(content, font=style.FONT_BODY, bg=style.BG_INPUT, fg=style.FG_DARK, bd=1, relief="solid")
        self.subject_list.pack(side="left", fill="both", expand=True, padx=(0, 12))
        controls = tk.Frame(content, bg=style.BG_CARD, width=250)
        controls.pack(side="right", fill="y")
        controls.pack_propagate(False)
        tk.Label(controls, text="New subject", font=style.FONT_LABEL, bg=style.BG_CARD, fg=style.FG_MUTED).pack(anchor="w")
        self.subject_entry = tk.Entry(controls, font=style.FONT_INPUT, bg=style.BG_INPUT, fg=style.FG_DARK)
        self.subject_entry.pack(fill="x", pady=(2, 8), ipady=3)
        self._button(controls, "Add subject", self.add_subject, success=True).pack(fill="x", pady=(0, 12))
        self._button(controls, "Remove selected", self.remove_subject, danger=True).pack(fill="x")
        tk.Label(controls, text="Subjects already linked to doubts are protected from deletion.", wraplength=220, justify="left", font=style.FONT_BODY, bg=style.BG_CARD, fg=style.FG_MUTED).pack(anchor="w", pady=(14, 0))

    def _button(self, parent, text, command, success=False, danger=False):
        color = style.COLOR_SUCCESS if success else style.COLOR_DANGER if danger else style.COLOR_PRIMARY
        return tk.Button(parent, text=text, command=command, font=style.FONT_LABEL, bg=color, fg="white", relief="flat", cursor="hand2", activeforeground="white")

    def refresh_all(self):
        for key, value in self.store.get_admin_metrics().items():
            self.metric_vars[key].set(value)
        self.doubt_tree.delete(*self.doubt_tree.get_children())
        for doubt in self.store.get_all_doubts():
            self.doubt_tree.insert("", "end", iid=str(doubt["id"]), values=(doubt["id"], doubt["student"], doubt["subject"], doubt["teacher"] or "Unassigned", doubt["severity"], f"⭐ {doubt.get('student_points', 0)}", doubt["status"]))
        self.user_tree.delete(*self.user_tree.get_children())
        for user in self.store.get_users():
            status = "Active" if user["active"] else "Deactivated"
            self.user_tree.insert("", "end", iid=user["username"], values=(user["username"], user["role"].title(), status))
        teachers = self.store.get_teachers()
        self.teacher_combo["values"] = teachers
        self.subject_list.delete(0, "end")
        for subject in self.store.get_subjects():
            self.subject_list.insert("end", subject)

    def _on_doubt_selected(self, _event=None):
        selected = self.doubt_tree.selection()
        if not selected:
            return
        self.selected_doubt_id = int(selected[0])
        doubt = next((d for d in self.store.get_all_doubts() if d["id"] == self.selected_doubt_id), None)
        if doubt:
            self.doubt_detail.set(f"#{doubt['id']} from {doubt['student']}\n\n{doubt['desc']}")
            self.teacher_var.set(doubt["teacher"])
            self.status_var.set(doubt["status"])

    def _selected_username(self):
        selected = self.user_tree.selection()
        return selected[0] if selected else None

    def _on_user_selected(self, _event=None):
        username = self._selected_username()
        if not username:
            return
        user = next(u for u in self.store.get_users() if u["username"] == username)
        self.user_detail.set(f"{username}\nRole: {user['role'].title()}\nAccess: {'Active' if user['active'] else 'Deactivated'}")
        self.role_var.set(user["role"])
        self.access_btn.config(text="Deactivate account" if user["active"] else "Reactivate account")

    def assign_selected(self):
        if self.selected_doubt_id is None or not self.teacher_var.get():
            messagebox.showwarning("Assignment", "Select a doubt and a teacher first.")
            return
        self.store.assign_doubt(self.selected_doubt_id, self.teacher_var.get())
        self.refresh_all()

    def update_status(self):
        if self.selected_doubt_id is None:
            messagebox.showwarning("Status", "Select a doubt first.")
            return
        self.store.set_doubt_status(self.selected_doubt_id, self.status_var.get())
        self.refresh_all()

    def update_role(self):
        username = self._selected_username()
        if not username:
            messagebox.showwarning("Role", "Select an account first.")
            return
        self.store.set_user_role(username, self.role_var.get())
        self.refresh_all()

    def toggle_access(self):
        username = self._selected_username()
        if not username:
            messagebox.showwarning("Account", "Select an account first.")
            return
        user = next(u for u in self.store.get_users() if u["username"] == username)
        if username == self.username and user["active"]:
            messagebox.showwarning("Account", "You cannot deactivate the account currently administering the system.")
            return
        self.store.set_user_active(username, not user["active"])
        self.refresh_all()

    def add_subject(self):
        if not self.store.add_subject(self.subject_entry.get()):
            messagebox.showwarning("Subject", "Enter a unique subject name.")
            return
        self.subject_entry.delete(0, "end")
        self.refresh_all()

    def remove_subject(self):
        selected = self.subject_list.curselection()
        if not selected:
            messagebox.showwarning("Subject", "Select a subject first.")
            return
        subject = self.subject_list.get(selected[0])
        if not self.store.remove_subject(subject):
            messagebox.showwarning("Subject", "This subject is still used by a doubt and cannot be removed.")
            return
        self.refresh_all()
