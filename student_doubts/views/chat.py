import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from . import style


class FeaturedDoubtDialog(tk.Toplevel):
    """A read-only, privacy-conscious view of a teacher-curated discussion."""

    def __init__(self, parent, store, doubt):
        super().__init__(parent)
        self.store = store
        self.doubt = doubt
        self.title(f"Featured doubt — {doubt['subject']}")
        self.configure(bg=style.BG_MAIN)
        self.transient(parent.winfo_toplevel())
        self.grab_set()
        self.minsize(620, 480)
        self.geometry("720x590")
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self._build()

    def _build(self):
        header = tk.Frame(self, bg="#ede9fe", padx=16, pady=12)
        header.pack(fill="x")
        tk.Label(header, text="📌 Featured learning discussion", font=style.FONT_TITLE,
                 bg="#ede9fe", fg="#5b21b6").pack(anchor="w")
        tk.Label(header, text=f"{self.doubt['subject']}  •  {self.doubt['status']}",
                 font=style.FONT_LABEL, bg="#ede9fe", fg=style.FG_MUTED).pack(anchor="w", pady=(3, 0))
        note = self.doubt.get("featured_note", "").strip()
        if note:
            tk.Label(header, text=f"Why it was shared: {note}", wraplength=670,
                     justify="left", font=style.FONT_BODY, bg="#ede9fe", fg=style.FG_DARK).pack(anchor="w", pady=(7, 0))

        body = tk.Frame(self, bg=style.BG_MAIN)
        body.pack(fill="both", expand=True, padx=14, pady=12)
        scrollbar = ttk.Scrollbar(body)
        scrollbar.pack(side="right", fill="y")
        transcript = tk.Text(body, wrap="word", state="normal", bg=style.BG_CARD,
                             fg=style.FG_DARK, font=style.FONT_INPUT,
                             yscrollcommand=scrollbar.set, bd=1, relief="solid",
                             padx=14, pady=12)
        transcript.pack(fill="both", expand=True)
        scrollbar.config(command=transcript.yview)
        transcript.tag_configure("student", foreground=style.COLOR_PRIMARY, font=style.FONT_LABEL)
        transcript.tag_configure("teacher", foreground=style.COLOR_SUCCESS, font=style.FONT_LABEL)
        transcript.tag_configure("meta", foreground=style.FG_MUTED, font=style.FONT_BODY)
        transcript.tag_configure("divider", foreground=style.BORDER_COLOR)

        # Student names are intentionally not shared with the wider student community.
        self._entry(transcript, "Student's question", self.doubt.get("desc", ""), "student")
        reply = self.doubt.get("reply", "").strip()
        if reply:
            self._entry(transcript, f"{self.doubt.get('teacher', 'Teacher')}'s reply", reply, "teacher")
        for message in self.store.get_chat_messages(self.doubt["id"]):
            is_student = message["sender"] == self.doubt.get("student")
            speaker = "Student" if is_student else self.doubt.get("teacher", "Teacher")
            self._entry(transcript, f"{speaker}  •  {message['timestamp']}", message["message"],
                        "student" if is_student else "teacher")
        transcript.config(state="disabled")

        footer = tk.Frame(self, bg=style.BG_MAIN)
        footer.pack(fill="x", padx=14, pady=(0, 12))
        tk.Label(footer, text="Read-only shared discussion", font=style.FONT_BODY,
                 bg=style.BG_MAIN, fg=style.FG_MUTED).pack(side="left")
        tk.Button(footer, text="Close", font=style.FONT_LABEL, bg=style.COLOR_PRIMARY,
                  fg="white", relief="flat", cursor="hand2", command=self.destroy).pack(side="right", ipadx=14, ipady=3)

    @staticmethod
    def _entry(transcript, heading, content, tag):
        transcript.insert("end", f"{heading}\n", tag)
        transcript.insert("end", f"{content}\n\n")
        transcript.insert("end", "─" * 64 + "\n", "divider")

class ChatFrame(tk.Frame):
    def __init__(self, parent, store, doubt_id, current_user, on_back):
        super().__init__(parent, bg=style.BG_MAIN)
        self.store = store
        self.doubt_id = doubt_id
        self.current_user = current_user
        self.on_back = on_back

        # Fetch doubt details
        self.doubt = next((d for d in self.store.get_all_doubts() if d["id"] == self.doubt_id), None)
        if not self.doubt:
            messagebox.showerror("Error", "Doubt not found.")
            self.on_back()
            return

        self.setup_ui()
        self.load_messages()

    def setup_ui(self):
        # 1. Header Frame
        header = tk.Frame(self, bg=style.BG_CARD, bd=1, relief="solid")
        header.pack(fill="x", side="top", ipady=5)
        self.header = header

        # Back Button
        back_btn = tk.Button(
            header,
            text="← Back to List",
            font=style.FONT_LABEL,
            bg=style.BG_INPUT,
            fg=style.FG_MUTED,
            relief="flat",
            cursor="hand2",
            command=self.on_back
        )
        back_btn.pack(side="left", padx=10, pady=5)

        # Title/Info Info Panel
        info_text = f"Subject: {self.doubt.get('subject')}  |  Student: {self.doubt.get('student')}  |  Teacher: {self.doubt.get('teacher')}"
        info_lbl = tk.Label(
            header,
            text=info_text,
            font=style.FONT_TITLE,
            bg=style.BG_CARD,
            fg=style.FG_DARK
        )
        info_lbl.pack(side="left", padx=20)

        # Status and Action buttons
        status = self.doubt.get("status", "Pending")
        self.status_var = tk.StringVar(value=f"Status: {status}")
        self.status_lbl = tk.Label(
            header,
            textvariable=self.status_var,
            font=style.FONT_LABEL,
            bg=style.BG_CARD,
            fg=style.COLOR_PRIMARY if status != "Resolved" else style.COLOR_SUCCESS
        )
        self.status_lbl.pack(side="right", padx=15, pady=5)

        self.action_btn = None
        self.update_status_buttons()

        # Recognition controls only appear in the teacher's own conversation.
        # They make the gamified layer part of a real interaction, not a separate
        # administrative task.
        if self.current_user == self.doubt.get("teacher"):
            self.points_var = tk.StringVar(value=str(self.doubt.get("student_points", 0)))
            self.points_combo = ttk.Combobox(header, textvariable=self.points_var,
                                             values=tuple(str(n) for n in range(11)),
                                             state="readonly", width=3)
            self.points_combo.pack(side="right", padx=(0, 4), pady=5)
            tk.Button(header, text="⭐ Award points", font=style.FONT_LABEL,
                      bg="#f59e0b", fg="white", relief="flat", cursor="hand2",
                      command=self.award_points).pack(side="right", padx=(8, 0), pady=5)
            self.feature_btn = tk.Button(
                header,
                text="📌 Unfeature" if self.doubt.get("featured") else "📌 Feature",
                font=style.FONT_LABEL, bg="#8b5cf6", fg="white", relief="flat",
                cursor="hand2", command=self.toggle_feature,
            )
            self.feature_btn.pack(side="right", padx=(8, 0), pady=5)

        # 2. Scrollable Messages Area
        self.msg_container = tk.Frame(self, bg=style.BG_MAIN)
        self.msg_container.pack(fill="both", expand=True, padx=10, pady=10)

        self.scrollbar = ttk.Scrollbar(self.msg_container)
        self.scrollbar.pack(side="right", fill="y")

        self.text_area = tk.Text(
            self.msg_container,
            wrap="word",
            state="disabled",
            bg=style.BG_CARD,
            fg=style.FG_DARK,
            font=style.FONT_INPUT,
            yscrollcommand=self.scrollbar.set,
            bd=1,
            relief="solid",
            padx=10,
            pady=10
        )
        self.text_area.pack(fill="both", expand=True)
        self.scrollbar.config(command=self.text_area.yview)

        # Tags configuration
        self.text_area.tag_configure("system_title", foreground=style.FG_MUTED, font=style.FONT_LABEL)
        self.text_area.tag_configure("student_title", foreground=style.COLOR_PRIMARY, font=style.FONT_LABEL)
        self.text_area.tag_configure("teacher_title", foreground=style.COLOR_SUCCESS, font=style.FONT_LABEL)
        self.text_area.tag_configure("body", font=style.FONT_INPUT)
        self.text_area.tag_configure("time", foreground="#94a3b8", font=("Helvetica", 8))
        self.text_area.tag_configure("divider", foreground=style.BORDER_COLOR, font=("Helvetica", 6))

        # 3. Input Message Area
        input_frame = tk.Frame(self, bg=style.BG_CARD, bd=1, relief="solid")
        input_frame.pack(fill="x", side="bottom", ipady=5)

        self.entry_msg = tk.Entry(
            input_frame,
            font=style.FONT_INPUT,
            bg=style.BG_INPUT,
            fg=style.FG_DARK,
            bd=1,
            relief="solid"
        )
        self.entry_msg.pack(side="left", fill="x", expand=True, padx=(15, 10), pady=10)
        self.entry_msg.bind("<Return>", lambda e: self.send_message())
        self.entry_msg.focus_set()

        send_btn = tk.Button(
            input_frame,
            text="Send",
            font=style.FONT_LABEL,
            bg=style.COLOR_PRIMARY,
            fg="white",
            activebackground="#2563eb",
            relief="flat",
            cursor="hand2",
            command=self.send_message
        )
        send_btn.pack(side="right", padx=(0, 15), pady=10, ipadx=15)

    def load_messages(self):
        # Enable text editing
        self.text_area.config(state="normal")
        self.text_area.delete("1.0", "end")

        # 1. Add Original Doubt
        self.text_area.insert("end", f"Original Doubt by {self.doubt.get('student')}\n", "student_title")
        self.text_area.insert("end", f"{self.doubt.get('desc')}\n", "body")
        self.text_area.insert("end", "─" * 60 + "\n", "divider")

        # 2. Add Teacher's Initial Reply only if it exists (for historical data)
        reply = self.doubt.get('reply', '').strip()
        if reply:
            self.text_area.insert("end", f"Initial Reply by {self.doubt.get('teacher')}\n", "teacher_title")
            self.text_area.insert("end", f"{reply}\n", "body")
            self.text_area.insert("end", "─" * 60 + "\n", "divider")

        # 3. Add Subsequent Chat Messages
        messages = self.store.get_chat_messages(self.doubt_id)
        for msg in messages:
            sender = msg["sender"]
            text = msg["message"]
            timestamp = msg["timestamp"]

            # Determine tag based on sender
            # Find if sender is student or teacher or match current role
            # For simplicity, if sender matches the student of the doubt, color primary, else success
            is_student = (sender == self.doubt.get("student"))
            title_tag = "student_title" if is_student else "teacher_title"
            
            self.text_area.insert("end", f"{sender} ", title_tag)
            self.text_area.insert("end", f"({timestamp})\n", "time")
            self.text_area.insert("end", f"{text}\n\n", "body")

        self.text_area.config(state="disabled")
        self.text_area.see("end")

    def send_message(self):
        text = self.entry_msg.get().strip()
        if not text:
            return

        try:
            self.store.add_chat_message(self.doubt_id, self.current_user, text)
            self.entry_msg.delete(0, "end")
            self.load_messages()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send message: {e}")

    def award_points(self):
        points = int(self.points_var.get())
        if self.store.award_student_points(self.doubt_id, points):
            self.doubt["student_points"] = points
            messagebox.showinfo("Student recognition", f"⭐ {points}/10 points awarded to {self.doubt['student']}.")

    def toggle_feature(self):
        if self.doubt.get("featured"):
            self.store.set_featured_doubt(self.doubt_id, False)
            self.doubt["featured"] = False
            self.doubt["featured_note"] = ""
            self.feature_btn.config(text="📌 Feature")
            return
        note = simpledialog.askstring(
            "Feature doubt", "Why is this doubt worth sharing? (optional)", parent=self
        )
        if note is None:
            return
        self.store.set_featured_doubt(self.doubt_id, True, note)
        self.doubt["featured"] = True
        self.doubt["featured_note"] = note.strip()
        self.feature_btn.config(text="📌 Unfeature")
        messagebox.showinfo("Featured doubt", "📌 This doubt is now visible to every student.")

    def update_status_buttons(self):
        if hasattr(self, "action_btn") and self.action_btn:
            self.action_btn.pack_forget()
            self.action_btn.destroy()
            self.action_btn = None

        status = self.doubt.get("status", "Pending")
        self.status_var.set(f"Status: {status}")
        
        if status == "Resolved":
            self.status_lbl.config(fg=style.COLOR_SUCCESS)
            # Both teachers and students can unresolve
            self.action_btn = tk.Button(
                self.header,
                text="↺ Unresolve",
                font=style.FONT_LABEL,
                bg=style.COLOR_PRIMARY,
                fg="white",
                relief="flat",
                cursor="hand2",
                command=self.unresolve_doubt
            )
            self.action_btn.pack(side="right", padx=10, pady=5)
        else:
            self.status_lbl.config(fg=style.COLOR_PRIMARY)
            self.action_btn = tk.Button(
                self.header,
                text="✔ Resolve",
                font=style.FONT_LABEL,
                bg=style.COLOR_SUCCESS,
                fg="white",
                relief="flat",
                cursor="hand2",
                command=self.resolve_doubt
            )
            self.action_btn.pack(side="right", padx=10, pady=5)

    def resolve_doubt(self):
        if messagebox.askyesno("Resolve Doubt", "Are you sure you want to mark this doubt as Resolved?"):
            try:
                self.store.resolve_doubt(self.doubt_id)
                self.doubt["status"] = "Resolved"
                self.update_status_buttons()
                messagebox.showinfo("Success", "Doubt has been marked as Resolved.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to resolve doubt: {e}")

    def unresolve_doubt(self):
        if messagebox.askyesno("Unresolve Doubt", "Are you sure you want to unresolve this doubt?"):
            try:
                self.store.unresolve_doubt(self.doubt_id)
                self.doubt["status"] = "Pending"
                self.update_status_buttons()
                messagebox.showinfo("Success", "Doubt has been marked as Unresolved.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to unresolve doubt: {e}")
