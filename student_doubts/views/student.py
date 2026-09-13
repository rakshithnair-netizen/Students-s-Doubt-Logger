import tkinter as tk
from tkinter import ttk, messagebox
from . import style
from .chat import ChatFrame, FeaturedDoubtDialog

class StudentDashboardFrame(tk.Frame):
    def __init__(self, parent, store, username):
        super().__init__(parent, bg=style.BG_MAIN)
        self.store = store
        self.username = username

        self.setup_ui()

    def setup_ui(self):
        # Container frame
        main_container = tk.Frame(self, bg=style.BG_MAIN)
        main_container.pack(fill="both", expand=True, padx=15, pady=15)

        # ──────────────────────────────────────────────────────────
        # LEFT PANE: Form Input
        # ──────────────────────────────────────────────────────────
        left_frame = tk.LabelFrame(
            main_container,
            text="Submit a New Doubt",
            font=style.FONT_TITLE,
            bg=style.BG_CARD,
            fg=style.FG_DARK,
            padx=15,
            pady=10,
            bd=1,
            relief="solid",
            width=350
        )
        left_frame.pack(side="left", fill="both", padx=(0, 10))
        left_frame.pack_propagate(False)

        # Subject Combobox
        tk.Label(left_frame, text="Subject", font=style.FONT_LABEL, bg=style.BG_CARD, fg=style.FG_MUTED).pack(anchor="w", pady=(5, 2))
        self.subj_combo = ttk.Combobox(left_frame, values=self.store.get_subjects(), state="readonly", font=style.FONT_INPUT)
        self.subj_combo.pack(fill="x", pady=(0, 10))
        self.subj_combo.set("Select Subject")
        self.subj_combo.bind("<<ComboboxSelected>>", lambda _event: self.update_teacher_choices())

        # Teacher Combobox
        tk.Label(left_frame, text="Preferred teacher (optional for fastest routing)", font=style.FONT_LABEL, bg=style.BG_CARD, fg=style.FG_MUTED).pack(anchor="w", pady=(5, 2))
        self.teacher_combo = ttk.Combobox(left_frame, state="disabled", font=style.FONT_INPUT)
        self.teacher_combo.pack(fill="x", pady=(0, 10))
        self.teacher_combo.set("Select Teacher")

        tk.Label(left_frame, text="Resolution preference", font=style.FONT_LABEL, bg=style.BG_CARD, fg=style.FG_MUTED).pack(anchor="w", pady=(2, 2))
        self.assignment_preference = tk.StringVar(value="Preferred teacher")
        preference_frame = tk.Frame(left_frame, bg=style.BG_CARD)
        preference_frame.pack(fill="x", pady=(0, 10))
        tk.Radiobutton(preference_frame, text="Preferred teacher", variable=self.assignment_preference,
                       value="Preferred teacher", bg=style.BG_CARD, activebackground=style.BG_CARD,
                       command=self._update_assignment_preference).pack(anchor="w")
        tk.Radiobutton(preference_frame, text="Fastest available", variable=self.assignment_preference,
                       value="Fastest available", bg=style.BG_CARD, activebackground=style.BG_CARD,
                       command=self._update_assignment_preference).pack(anchor="w")
        self.assignment_hint = tk.StringVar(value="Your chosen teacher will receive this doubt.")
        tk.Label(left_frame, textvariable=self.assignment_hint, wraplength=310, justify="left",
                 font=style.FONT_BODY, bg=style.BG_CARD, fg=style.FG_MUTED).pack(anchor="w", pady=(0, 10))

        # Severity level Radio buttons
        tk.Label(left_frame, text="Severity Level", font=style.FONT_LABEL, bg=style.BG_CARD, fg=style.FG_MUTED).pack(anchor="w", pady=(5, 2))
        severity_frame = tk.Frame(left_frame, bg=style.BG_CARD)
        severity_frame.pack(fill="x", pady=(0, 10))
        self.severity = tk.StringVar(value="Low")

        tk.Radiobutton(severity_frame, text="Low", variable=self.severity, value="Low", bg=style.BG_CARD, activebackground=style.BG_CARD).pack(side="left", expand=True, anchor="w")
        tk.Radiobutton(severity_frame, text="Medium", variable=self.severity, value="Medium", bg=style.BG_CARD, activebackground=style.BG_CARD).pack(side="left", expand=True, anchor="w")
        tk.Radiobutton(severity_frame, text="High", variable=self.severity, value="High", bg=style.BG_CARD, activebackground=style.BG_CARD).pack(side="left", expand=True, anchor="w")

        # Description text entry
        tk.Label(left_frame, text="Doubt Description", font=style.FONT_LABEL, bg=style.BG_CARD, fg=style.FG_MUTED).pack(anchor="w", pady=(5, 2))
        self.desc_t = tk.Text(left_frame, height=5, font=style.FONT_INPUT, bg=style.BG_INPUT, fg=style.FG_DARK, bd=1, relief="solid", wrap="word")
        self.desc_t.pack(fill="x", pady=(0, 15))

        # Submit button
        submit_btn = tk.Button(
            left_frame,
            text="Submit Doubt",
            font=style.FONT_LABEL,
            bg=style.COLOR_PRIMARY,
            fg="white",
            activebackground="#2563eb",
            relief="flat",
            cursor="hand2",
            command=self.submit_doubt
        )
        submit_btn.config(highlightbackground=style.BG_CARD)
        submit_btn.pack(fill="x", ipady=5)

        # ──────────────────────────────────────────────────────────
        # RIGHT PANE: My doubts list Treeview
        # ──────────────────────────────────────────────────────────
        right_frame = tk.LabelFrame(
            main_container,
            text="My Submitted Doubts",
            font=style.FONT_TITLE,
            bg=style.BG_CARD,
            fg=style.FG_DARK,
            padx=10,
            pady=10,
            bd=1,
            relief="solid"
        )
        right_frame.pack(side="left", fill="both", expand=True)
        self.right_frame = right_frame

        self._build_community_sidebar(main_container)

        # List controls stay separate from the submission form so students can
        # quickly find a past doubt without losing what they are currently writing.
        self.search_var = tk.StringVar()
        self.subject_filter_var = tk.StringVar(value="All subjects")
        self.teacher_filter_var = tk.StringVar(value="All teachers")
        self.status_filter_var = tk.StringVar(value="All statuses")
        self.sort_var = tk.StringVar(value="Newest first")

        self.filter_frame = tk.Frame(right_frame, bg=style.BG_CARD)
        self.filter_frame.pack(fill="x", pady=(0, 8))

        tk.Label(self.filter_frame, text="Find", font=style.FONT_LABEL,
                 bg=style.BG_CARD, fg=style.FG_MUTED).pack(side="left", padx=(0, 4))
        search_entry = tk.Entry(self.filter_frame, textvariable=self.search_var,
                                font=style.FONT_BODY, width=16)
        search_entry.pack(side="left", padx=(0, 8))
        search_entry.bind("<KeyRelease>", lambda _event: self.refresh_list())

        self.subject_filter_combo = self._make_filter_combo(self.filter_frame, self.subject_filter_var, 13)
        self.teacher_filter_combo = self._make_filter_combo(self.filter_frame, self.teacher_filter_var, 13)
        self.status_filter_combo = self._make_filter_combo(self.filter_frame, self.status_filter_var, 13)
        self.sort_combo = self._make_filter_combo(self.filter_frame, self.sort_var, 16)

        tk.Button(self.filter_frame, text="Clear", font=style.FONT_BODY,
                  bg=style.BG_MAIN, fg=style.FG_DARK, relief="flat", cursor="hand2",
                  command=self.clear_filters).pack(side="left", padx=(6, 0))

        tree_container = tk.Frame(right_frame, bg=style.BG_CARD)
        tree_container.pack(fill="both", expand=True)
        self.tree_container = tree_container

        cols = ("ID", "Subject", "Teacher", "Severity", "Points", "Description", "Status")
        self.tree = ttk.Treeview(tree_container, columns=cols, show="headings")

        # Vertical & horizontal scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        # Sizing and headers
        col_widths = {
            "ID": 40,
            "Subject": 80,
            "Teacher": 100,
            "Severity": 90,
            "Points": 65,
            "Description": 200,
            "Status": 150
        }

        for col in cols:
            self.tree.heading(col, text=col, anchor="w")
            self.tree.column(col, width=col_widths[col], minwidth=50, stretch=True)

        self.tree.bind("<Double-1>", self.on_double_click)

        # Button frame at the bottom of the student dashboard right pane
        btn_frame = tk.Frame(right_frame, bg=style.BG_CARD)
        btn_frame.pack(fill="x", pady=(10, 0))
        self.btn_frame = btn_frame

        open_chat_btn = tk.Button(
            btn_frame,
            text="💬 Open Chat",
            font=style.FONT_LABEL,
            bg=style.COLOR_PRIMARY,
            fg="white",
            activebackground="#2563eb",
            relief="flat",
            cursor="hand2",
            command=self.open_chat_for_selected
        )
        open_chat_btn.config(highlightbackground=style.BG_CARD)
        open_chat_btn.pack(side="left", padx=(0, 10), ipady=3, ipadx=10)

        self.unresolve_btn = tk.Button(
            btn_frame,
            text="↺ Unresolve Doubt",
            font=style.FONT_LABEL,
            bg=style.COLOR_PRIMARY,
            fg="white",
            relief="flat",
            cursor="hand2",
            command=self.unresolve_selected_doubt
        )
        self.unresolve_btn.config(highlightbackground=style.BG_CARD)
        self.unresolve_btn.pack(side="left", ipady=3, ipadx=10)

        self.refresh_list()

    def _build_community_sidebar(self, parent):
        sidebar = tk.LabelFrame(parent, text="🏆 Community", font=style.FONT_TITLE,
                                bg=style.BG_CARD, fg=style.FG_DARK, padx=10, pady=10,
                                bd=1, relief="solid", width=250)
        sidebar.pack(side="right", fill="both", padx=(10, 0))
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="Student leaderboard", font=style.FONT_LABEL,
                 bg=style.BG_CARD, fg=style.FG_MUTED).pack(anchor="w")
        self.leaderboard = tk.Listbox(sidebar, height=7, font=style.FONT_BODY,
                                      bg=style.BG_INPUT, fg=style.FG_DARK, bd=1, relief="solid")
        self.leaderboard.pack(fill="x", pady=(4, 12))

        tk.Label(sidebar, text="📌 Featured doubts", font=style.FONT_LABEL,
                 bg=style.BG_CARD, fg=style.FG_MUTED).pack(anchor="w")
        self.feature_subject_var = tk.StringVar(value="All subjects")
        self.feature_subject_combo = ttk.Combobox(sidebar, textvariable=self.feature_subject_var,
                                                  state="readonly", font=style.FONT_BODY)
        self.feature_subject_combo.pack(fill="x", pady=(3, 5))
        self.feature_subject_combo.bind("<<ComboboxSelected>>", lambda _event: self.refresh_featured())
        self.featured_list = tk.Listbox(sidebar, font=style.FONT_BODY, bg=style.BG_INPUT,
                                        fg=style.FG_DARK, bd=1, relief="solid")
        self.featured_list.pack(fill="both", expand=True)
        self.featured_list.bind("<ButtonRelease-1>", self.open_featured_doubt)
        self.featured_list.bind("<Return>", self.open_featured_doubt)
        tk.Label(sidebar, text="Click a shared discussion to read it. Student names stay private.", wraplength=215,
                 justify="left", font=style.FONT_BODY, bg=style.BG_CARD, fg=style.FG_MUTED).pack(anchor="w", pady=(6, 0))

    def refresh_community(self):
        self.leaderboard.delete(0, "end")
        medals = ("🥇", "🥈", "🥉")
        for index, row in enumerate(self.store.get_student_leaderboard(), start=1):
            prefix = medals[index - 1] if index <= 3 else f"{index}."
            self.leaderboard.insert("end", f"{prefix} {row['student']} — {row['points']} pts")
        self.refresh_featured()

    def refresh_featured(self):
        doubts = self.store.get_featured_doubts()
        subjects = sorted({d["subject"] for d in doubts})
        self.feature_subject_combo["values"] = ["All subjects"] + subjects
        selected = self.feature_subject_var.get()
        self.featured_list.delete(0, "end")
        self.featured_doubts = []
        for doubt in doubts:
            if selected != "All subjects" and doubt["subject"] != selected:
                continue
            note = f" — {doubt['featured_note']}" if doubt.get("featured_note") else ""
            self.featured_list.insert("end", f"📌 {doubt['subject']}: {doubt['desc'][:55]}{note}")
            self.featured_doubts.append(doubt)

    def open_featured_doubt(self, _event=None):
        selection = self.featured_list.curselection()
        if selection:
            FeaturedDoubtDialog(self, self.store, self.featured_doubts[selection[0]])

    def _make_filter_combo(self, parent, variable, width):
        combo = ttk.Combobox(parent, textvariable=variable, state="readonly",
                             font=style.FONT_BODY, width=width)
        combo.pack(side="left", padx=(0, 5))
        combo.bind("<<ComboboxSelected>>", lambda _event: self.refresh_list())
        return combo

    def clear_filters(self):
        self.search_var.set("")
        self.subject_filter_var.set("All subjects")
        self.teacher_filter_var.set("All teachers")
        self.status_filter_var.set("All statuses")
        self.sort_var.set("Newest first")
        self.refresh_list()

    def _filtered_doubts(self):
        doubts = self.store.get_doubts_for_student(self.username)
        self.subject_filter_combo["values"] = ["All subjects"] + sorted({d["subject"] for d in doubts})
        self.teacher_filter_combo["values"] = ["All teachers"] + sorted({d.get("teacher", "") for d in doubts if d.get("teacher", "")})
        self.status_filter_combo["values"] = ["All statuses"] + sorted({d.get("status", "Pending") for d in doubts})
        self.sort_combo["values"] = ("Newest first", "Oldest first", "Severity: high to low",
                                      "Status", "Subject", "Teacher")

        search = self.search_var.get().strip().lower()
        doubts = [d for d in doubts if (
            self.subject_filter_var.get() == "All subjects" or d["subject"] == self.subject_filter_var.get()
        ) and (
            self.teacher_filter_var.get() == "All teachers" or d.get("teacher", "") == self.teacher_filter_var.get()
        ) and (
            self.status_filter_var.get() == "All statuses" or d.get("status", "Pending") == self.status_filter_var.get()
        ) and (
            not search or search in " ".join(str(d.get(key, "")) for key in ("id", "subject", "teacher", "severity", "desc", "status")).lower()
        )]

        severity_rank = {"High": 3, "Medium": 2, "Low": 1}
        sort_key = self.sort_var.get()
        if sort_key == "Oldest first":
            doubts.sort(key=lambda d: d["id"])
        elif sort_key == "Severity: high to low":
            doubts.sort(key=lambda d: (-severity_rank.get(d.get("severity"), 0), -d["id"]))
        elif sort_key == "Status":
            doubts.sort(key=lambda d: (d.get("status", ""), -d["id"]))
        elif sort_key == "Subject":
            doubts.sort(key=lambda d: (d.get("subject", "").lower(), -d["id"]))
        elif sort_key == "Teacher":
            doubts.sort(key=lambda d: (d.get("teacher", "").lower(), -d["id"]))
        else:
            doubts.sort(key=lambda d: d["id"], reverse=True)
        return doubts

    def refresh_list(self):
        self.tree.delete(*self.tree.get_children())
        for d in self._filtered_doubts():
            # Formatting badges for high readability & dark mode safety
            sev = d.get("severity", "Low")
            if sev == "High":
                sev_display = "🔴 High"
            elif sev == "Medium":
                sev_display = "🟡 Medium"
            else:
                sev_display = "🟢 Low"

            status = d.get("status", "Pending")
            status_badges = {
                "Pending": "⌛ Pending",
                "Assigned": "👤 Assigned",
                "Replied": "💬 Replied",
                "Resolved": "✅ Resolved",
            }
            status_display = status_badges.get(status, status)


            self.tree.insert("", "end", values=(
                d["id"],
                d["subject"],
                d.get("teacher", ""),
                sev_display,
                f"⭐ {d.get('student_points', 0)}",
                d["desc"],
                status_display
            ))
        self.refresh_community()

    def submit_doubt(self):
        s = self.subj_combo.get()
        t = self.teacher_combo.get()
        sev = self.severity.get()
        d = self.desc_t.get("1.0", "end").strip()
        preference = self.assignment_preference.get()

        if s == "Select Subject" or not d or not sev or (preference == "Preferred teacher" and t not in self.teacher_combo["values"]):
            messagebox.showwarning("Warning", "Please fill all fields before submitting.")
            return

        try:
            _, assigned_teacher = self.store.create_routed_doubt(self.username, s, preference, t if preference == "Preferred teacher" else "", sev, d)
        except ValueError as error:
            messagebox.showwarning("Routing unavailable", str(error))
            return

        # Clear inputs
        self.subj_combo.set("Select Subject")
        self.teacher_combo.set("Select Teacher")
        self.assignment_preference.set("Preferred teacher")
        self._update_assignment_preference()
        self.severity.set("Low")
        self.desc_t.delete("1.0", "end")

        self.refresh_list()
        messagebox.showinfo("Assigned", f"Your doubt was assigned to {assigned_teacher}.")

    def update_teacher_choices(self):
        subject = self.subj_combo.get()
        teachers = self.store.get_teachers_for_subject(subject) if subject != "Select Subject" else []
        self.teacher_combo["values"] = [teacher["username"] for teacher in teachers]
        self.teacher_combo.set("Select Teacher" if teachers else "No qualified teachers")
        if self.assignment_preference.get() == "Preferred teacher":
            self.teacher_combo.configure(state="readonly" if teachers else "disabled")
        if not teachers:
            self.assignment_hint.set("No teacher has selected this subject yet. Choose another subject or ask a teacher to add it.")
        elif self.assignment_preference.get() == "Preferred teacher":
            self.assignment_hint.set("Only teachers qualified for this subject are shown.")

    def _update_assignment_preference(self):
        fastest = self.assignment_preference.get() == "Fastest available"
        has_qualified_teacher = bool(self.store.get_teachers_for_subject(self.subj_combo.get())) if self.subj_combo.get() != "Select Subject" else False
        self.teacher_combo.configure(state="disabled" if fastest or not has_qualified_teacher else "readonly")
        self.assignment_hint.set(
            "The system will choose the least-loaded available teacher." if fastest
            else "Your chosen teacher will receive this doubt; you can switch to fastest available later if needed."
        )

    def get_selected_doubt_id(self):
        sel = self.tree.selection()
        if not sel:
            return None
        values = self.tree.item(sel[0], "values")
        if not values:
            return None
        try:
            return int(values[0])
        except (ValueError, TypeError):
            return None

    def on_double_click(self, event):
        item = self.tree.selection()
        if not item:
            return
        
        values = self.tree.item(item[0], "values")
        if not values:
            return
        
        try:
            doubt_id = int(values[0])
        except (ValueError, TypeError):
            return
        
        self.open_chat_by_id(doubt_id)

    def open_chat_for_selected(self):
        did = self.get_selected_doubt_id()
        if did is None:
            messagebox.showwarning("Warning", "Please select a doubt from the table to open chat.")
            return
        self.open_chat_by_id(did)

    def open_chat_by_id(self, doubt_id):
        if hasattr(self, "chat_frame") and self.chat_frame:
            return
            
        # Hide the treeview container and the button frame
        self.tree_container.pack_forget()
        self.filter_frame.pack_forget()
        if hasattr(self, "btn_frame") and self.btn_frame:
            self.btn_frame.pack_forget()
        
        # Create and pack the ChatFrame
        self.chat_frame = ChatFrame(
            self.right_frame,
            self.store,
            doubt_id,
            self.username,
            on_back=self.close_chat
        )
        self.chat_frame.pack(fill="both", expand=True)

    def close_chat(self):
        if hasattr(self, "chat_frame") and self.chat_frame:
            self.chat_frame.destroy()
            self.chat_frame = None
        
        # Restore treeview container, button frame and refresh list
        self.tree_container.pack(fill="both", expand=True)
        self.filter_frame.pack(fill="x", pady=(0, 8), before=self.tree_container)
        if hasattr(self, "btn_frame") and self.btn_frame:
            self.btn_frame.pack(fill="x", pady=(10, 0))
        self.refresh_list()

    def unresolve_selected_doubt(self):
        did = self.get_selected_doubt_id()
        if did is None:
            messagebox.showwarning("Warning", "Please select a doubt to unresolve.")
            return
        
        # Get doubt details to verify if it's resolved
        doubt = next((d for d in self.store.get_all_doubts() if d["id"] == did), None)
        if not doubt or doubt.get("status") != "Resolved":
            messagebox.showwarning("Warning", "Only resolved doubts can be unresolved.")
            return
            
        if messagebox.askyesno("Unresolve Doubt", "Are you sure you want to mark this doubt as Unresolved?"):
            self.store.unresolve_doubt(did)
            self.refresh_list()
            messagebox.showinfo("Success", "Doubt marked as Unresolved.")
