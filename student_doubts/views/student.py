import tkinter as tk
from tkinter import ttk, messagebox
from . import style
from .chat import ChatFrame

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

        # Teacher Combobox
        tk.Label(left_frame, text="Teacher", font=style.FONT_LABEL, bg=style.BG_CARD, fg=style.FG_MUTED).pack(anchor="w", pady=(5, 2))
        self.teacher_combo = ttk.Combobox(left_frame, values=self.store.get_teachers(), state="readonly", font=style.FONT_INPUT)
        self.teacher_combo.pack(fill="x", pady=(0, 10))
        self.teacher_combo.set("Select Teacher")

        # Severity level Radio buttons
        tk.Label(left_frame, text="Severity Level", font=style.FONT_LABEL, bg=style.BG_CARD, fg=style.FG_MUTED).pack(anchor="w", pady=(5, 2))
        severity_frame = tk.Frame(left_frame, bg=style.BG_CARD)
        severity_frame.pack(fill="x", pady=(0, 10))
        self.severity = tk.StringVar(value="Low")

        tk.Radiobutton(severity_frame, text="Low", variable=self.severity, value="Low", bg=style.BG_CARD, activebackground=style.BG_CARD).pack(side="left", expand=True, anchor="w")
        tk.Radiobutton(severity_frame, text="Medium", variable=self.severity, value="Medium", bg=style.BG_CARD, activebackground=style.BG_CARD).pack(side="left", expand=True, anchor="w")
        tk.Radiobutton(severity_frame, text="High", variable=self.severity, value="High", bg=style.BG_CARD, activebackground=style.BG_CARD).pack(side="left", expand=True, anchor="w")

        # Extra flags Checkbuttons
        tk.Label(left_frame, text="Additional Flags", font=style.FONT_LABEL, bg=style.BG_CARD, fg=style.FG_MUTED).pack(anchor="w", pady=(5, 2))
        flags_frame = tk.Frame(left_frame, bg=style.BG_CARD)
        flags_frame.pack(fill="x", pady=(0, 10))
        
        self.urgent_var = tk.IntVar()
        self.explain_var = tk.IntVar()

        tk.Checkbutton(flags_frame, text="Urgent", variable=self.urgent_var, bg=style.BG_CARD, activebackground=style.BG_CARD).pack(side="left", expand=True, anchor="w")
        tk.Checkbutton(flags_frame, text="Requires Detail", variable=self.explain_var, bg=style.BG_CARD, activebackground=style.BG_CARD).pack(side="left", expand=True, anchor="w")

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
        right_frame.pack(side="right", fill="both", expand=True)
        self.right_frame = right_frame

        tree_container = tk.Frame(right_frame, bg=style.BG_CARD)
        tree_container.pack(fill="both", expand=True)
        self.tree_container = tree_container

        cols = ("ID", "Subject", "Teacher", "Severity", "Urgent", "Needs Explanation", "Description", "Reply")
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
            "Urgent": 80,
            "Needs Explanation": 120,
            "Description": 200,
            "Reply": 150
        }

        for col in cols:
            self.tree.heading(col, text=col, anchor="w")
            self.tree.column(col, width=col_widths[col], minwidth=50, stretch=True)

        self.tree.bind("<Double-1>", self.on_double_click)
        self.refresh_list()

    def refresh_list(self):
        self.tree.delete(*self.tree.get_children())
        for d in self.store.get_doubts_for_student(self.username):
            # Formatting badges for high readability & dark mode safety
            sev = d.get("severity", "Low")
            if sev == "High":
                sev_display = "🔴 High"
            elif sev == "Medium":
                sev_display = "🟡 Medium"
            else:
                sev_display = "🟢 Low"

            urgent_display = "🚨 Urgent" if d.get("urgent") == "Yes" else "No"
            explain_display = "📝 Yes" if d.get("explain") == "Yes" else "No"

            status = d.get("status", "Pending")
            if status == "Resolved":
                reply_display = "✅ Resolved"
            else:
                reply_display = d["reply"] or "⌛ Pending"


            self.tree.insert("", "end", values=(
                d["id"],
                d["subject"],
                d.get("teacher", ""),
                sev_display,
                urgent_display,
                explain_display,
                d["desc"],
                reply_display
            ))

    def submit_doubt(self):
        s = self.subj_combo.get()
        t = self.teacher_combo.get()
        sev = self.severity.get()
        d = self.desc_t.get("1.0", "end").strip()

        urgent = "Yes" if self.urgent_var.get() == 1 else "No"
        explain = "Yes" if self.explain_var.get() == 1 else "No"

        if s == "Select Subject" or t == "Select Teacher" or not d or not sev:
            messagebox.showwarning("Warning", "Please fill all fields before submitting.")
            return

        self.store.add_doubt(self.username, s, t, sev, urgent, explain, d)

        # Clear inputs
        self.subj_combo.set("Select Subject")
        self.teacher_combo.set("Select Teacher")
        self.severity.set("Low")
        self.urgent_var.set(0)
        self.explain_var.set(0)
        self.desc_t.delete("1.0", "end")

        self.refresh_list()
        messagebox.showinfo("Success", "Doubt submitted successfully!")

    def on_double_click(self, event):
        item = self.tree.selection()
        if not item:
            return
        
        values = self.tree.item(item[0], "values")
        if not values:
            return
        
        reply = values[7]
        if reply == "⌛ Pending":
            messagebox.showinfo("Chat Not Available", "You can start chatting once the teacher replies to your doubt.")
            return
        
        try:
            doubt_id = int(values[0])
        except (ValueError, TypeError):
            return
        
        # Hide the treeview container
        self.tree_container.pack_forget()
        
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
        
        # Restore treeview container and refresh list
        self.tree_container.pack(fill="both", expand=True)
        self.refresh_list()

    def unresolve_selected_doubt(self):
        did = self.selected_doubt_id
        if did is None:
            messagebox.showwarning("Warning", "Please select a doubt to resolve.")
            return
        if messagebox.askyesno("Unresolve Doubt", "Are you sure you want to mark this doubt as Unresolved?"):
            self.store.resolve_doubt(did)
            self.clear_details()
            self.load_list()
            messagebox.showinfo("Success", "Doubt marked as solved.")