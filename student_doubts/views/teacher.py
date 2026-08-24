import tkinter as tk
from tkinter import ttk, messagebox
from . import style
from .chat import ChatFrame


class TeacherDashboardFrame(tk.Frame):
    def __init__(self, parent, store, username):
        super().__init__(parent, bg=style.BG_MAIN)
        self.store, self.username, self.selected_doubt_id = store, username, None
        self._build()
        self.load_list()

    def _build(self):
        self.main = tk.Frame(self, bg=style.BG_MAIN)
        self.main.pack(fill="both", expand=True, padx=15, pady=15)
        self.table_card = tk.LabelFrame(self.main, text="Student Doubts", font=style.FONT_TITLE, bg=style.BG_CARD, fg=style.FG_DARK, padx=10, pady=10, bd=1, relief="solid")
        self.table_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.search_var = tk.StringVar(); self.subject_var = tk.StringVar(value="All subjects")
        self.student_var = tk.StringVar(value="All students"); self.status_var = tk.StringVar(value="All statuses")
        self.sort_var = tk.StringVar(value="Newest first")
        controls = tk.Frame(self.table_card, bg=style.BG_CARD); controls.pack(fill="x", pady=(0, 8))
        tk.Label(controls, text="Find", font=style.FONT_LABEL, bg=style.BG_CARD, fg=style.FG_MUTED).pack(side="left", padx=(0, 4))
        entry = tk.Entry(controls, textvariable=self.search_var, font=style.FONT_BODY, width=14); entry.pack(side="left", padx=(0, 6)); entry.bind("<KeyRelease>", lambda _event: self.load_list())
        self.subject_combo = self._combo(controls, self.subject_var, 12); self.student_combo = self._combo(controls, self.student_var, 12)
        self.status_combo = self._combo(controls, self.status_var, 12); self.sort_combo = self._combo(controls, self.sort_var, 16)
        tk.Button(controls, text="Clear", font=style.FONT_BODY, bg=style.BG_MAIN, fg=style.FG_DARK, relief="flat", cursor="hand2", command=self.clear_filters).pack(side="left")

        holder = tk.Frame(self.table_card, bg=style.BG_CARD); holder.pack(fill="both", expand=True)
        cols = ("ID", "Student", "Subject", "Severity", "Points", "Description", "Status")
        self.tree = ttk.Treeview(holder, columns=cols, show="headings")
        widths = {"ID": 45, "Student": 95, "Subject": 95, "Severity": 85, "Points": 60, "Description": 245, "Status": 105}
        for col in cols: self.tree.heading(col, text=col, anchor="w"); self.tree.column(col, width=widths[col], minwidth=50, stretch=True)
        sy = ttk.Scrollbar(holder, orient="vertical", command=self.tree.yview); sx = ttk.Scrollbar(holder, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set); sy.pack(side="right", fill="y"); sx.pack(side="bottom", fill="x"); self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._select); self.tree.bind("<Double-1>", lambda _event: self.open_selected())
        actions = tk.Frame(self.table_card, bg=style.BG_CARD); actions.pack(fill="x", pady=(9, 0))
        tk.Button(actions, text="💬 Open selected chat", font=style.FONT_LABEL, bg=style.COLOR_PRIMARY, fg="white", relief="flat", cursor="hand2", command=self.open_selected).pack(side="left", ipadx=10, ipady=3)
        self._build_sidebar()

    def _build_sidebar(self):
        self.sidebar = tk.LabelFrame(self.main, text="🏆 Learning Community", font=style.FONT_TITLE, bg=style.BG_CARD, fg=style.FG_DARK, padx=10, pady=10, bd=1, relief="solid", width=255)
        self.sidebar.pack(side="right", fill="both"); self.sidebar.pack_propagate(False)
        tk.Label(self.sidebar, text="Student leaderboard", font=style.FONT_LABEL, bg=style.BG_CARD, fg=style.FG_MUTED).pack(anchor="w")
        self.leaderboard = tk.Listbox(self.sidebar, height=8, font=style.FONT_BODY, bg=style.BG_INPUT, fg=style.FG_DARK); self.leaderboard.pack(fill="x", pady=(4, 12))
        tk.Label(self.sidebar, text="📌 Featured doubts", font=style.FONT_LABEL, bg=style.BG_CARD, fg=style.FG_MUTED).pack(anchor="w")
        self.feature_subject_var = tk.StringVar(value="All subjects")
        self.feature_subject = ttk.Combobox(self.sidebar, textvariable=self.feature_subject_var, state="readonly", font=style.FONT_BODY); self.feature_subject.pack(fill="x", pady=(3, 5)); self.feature_subject.bind("<<ComboboxSelected>>", lambda _event: self.refresh_featured())
        self.featured = tk.Listbox(self.sidebar, font=style.FONT_BODY, bg=style.BG_INPUT, fg=style.FG_DARK); self.featured.pack(fill="both", expand=True)
        tk.Label(self.sidebar, text="Open a chat to award ⭐ points or share a great doubt.", wraplength=220, justify="left", font=style.FONT_BODY, bg=style.BG_CARD, fg=style.FG_MUTED).pack(anchor="w", pady=(6, 0))

    def _combo(self, parent, variable, width):
        combo = ttk.Combobox(parent, textvariable=variable, state="readonly", font=style.FONT_BODY, width=width); combo.pack(side="left", padx=(0, 4)); combo.bind("<<ComboboxSelected>>", lambda _event: self.load_list()); return combo

    def clear_filters(self):
        for variable, value in ((self.search_var, ""), (self.subject_var, "All subjects"), (self.student_var, "All students"), (self.status_var, "All statuses"), (self.sort_var, "Newest first")): variable.set(value)
        self.load_list()

    def _filtered_doubts(self):
        doubts = self.store.get_doubts_for_teacher(self.username)
        self.subject_combo["values"] = ["All subjects"] + sorted({d["subject"] for d in doubts}); self.student_combo["values"] = ["All students"] + sorted({d["student"] for d in doubts}); self.status_combo["values"] = ["All statuses"] + sorted({d["status"] for d in doubts})
        self.sort_combo["values"] = ("Newest first", "Oldest first", "Severity: high to low", "Status", "Subject", "Student", "Highest points")
        query = self.search_var.get().strip().lower()
        doubts = [d for d in doubts if (self.subject_var.get() == "All subjects" or d["subject"] == self.subject_var.get()) and (self.student_var.get() == "All students" or d["student"] == self.student_var.get()) and (self.status_var.get() == "All statuses" or d["status"] == self.status_var.get()) and (not query or query in " ".join(str(d.get(k, "")) for k in ("id", "student", "subject", "severity", "desc", "status")).lower())]
        severity = {"High": 3, "Medium": 2, "Low": 1}; sort = self.sort_var.get()
        if sort == "Oldest first": doubts.sort(key=lambda d: d["id"])
        elif sort == "Severity: high to low": doubts.sort(key=lambda d: (-severity.get(d["severity"], 0), -d["id"]))
        elif sort == "Status": doubts.sort(key=lambda d: (d["status"], -d["id"]))
        elif sort == "Subject": doubts.sort(key=lambda d: (d["subject"].lower(), -d["id"]))
        elif sort == "Student": doubts.sort(key=lambda d: (d["student"].lower(), -d["id"]))
        elif sort == "Highest points": doubts.sort(key=lambda d: (-d.get("student_points", 0), -d["id"]))
        else: doubts.sort(key=lambda d: d["id"], reverse=True)
        return doubts

    def load_list(self):
        self.selected_doubt_id = None; self.tree.delete(*self.tree.get_children())
        for d in self._filtered_doubts():
            badge = {"High": "🔴 High", "Medium": "🟡 Medium", "Low": "🟢 Low"}.get(d["severity"], d["severity"]); status = {"Pending": "⌛ Pending", "Assigned": "👤 Assigned", "Replied": "💬 Replied", "Resolved": "✅ Resolved"}.get(d["status"], d["status"])
            self.tree.insert("", "end", iid=str(d["id"]), values=(d["id"], d["student"], d["subject"], badge, f"⭐ {d.get('student_points', 0)}", d["desc"], status))
        self.refresh_community()

    def refresh_community(self):
        self.leaderboard.delete(0, "end"); medals = ("🥇", "🥈", "🥉")
        for index, row in enumerate(self.store.get_student_leaderboard(), 1): self.leaderboard.insert("end", f"{medals[index - 1] if index <= 3 else str(index) + '.'} {row['student']} — {row['points']} pts")
        self.refresh_featured()

    def refresh_featured(self):
        doubts = self.store.get_featured_doubts(); self.feature_subject["values"] = ["All subjects"] + sorted({d["subject"] for d in doubts}); self.featured.delete(0, "end")
        for d in doubts:
            if self.feature_subject_var.get() == "All subjects" or d["subject"] == self.feature_subject_var.get(): self.featured.insert("end", f"📌 {d['subject']}: {d['desc'][:58]}")

    def _select(self, _event=None):
        selected = self.tree.selection(); self.selected_doubt_id = int(selected[0]) if selected else None

    def open_selected(self):
        if self.selected_doubt_id is None: messagebox.showwarning("Open chat", "Select a doubt first."); return
        self.table_card.pack_forget(); self.sidebar.pack_forget(); self.chat_frame = ChatFrame(self.main, self.store, self.selected_doubt_id, self.username, self.close_chat); self.chat_frame.pack(fill="both", expand=True)

    def close_chat(self):
        self.chat_frame.destroy(); self.table_card.pack(side="left", fill="both", expand=True, padx=(0, 10)); self.sidebar.pack(side="right", fill="both"); self.load_list()
