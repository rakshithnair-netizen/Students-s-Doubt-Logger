import tkinter as tk
from tkinter import ttk, messagebox
from . import style

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

        # Resolve Button (Visible only to teachers if not already resolved)
        is_teacher = self.current_user in self.store.get_teachers()
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

        if is_teacher and status != "Resolved":
            self.resolve_btn = tk.Button(
                header,
                text="✔ Resolve",
                font=style.FONT_LABEL,
                bg=style.COLOR_SUCCESS,
                fg="white",
                relief="flat",
                cursor="hand2",
                command=self.resolve_doubt
            )
            self.resolve_btn.pack(side="right", padx=10, pady=5)

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

        # 2. Add Teacher's Initial Reply
        self.text_area.insert("end", f"Initial Reply by {self.doubt.get('teacher')}\n", "teacher_title")
        self.text_area.insert("end", f"{self.doubt.get('reply')}\n", "body")
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

    def resolve_doubt(self):
        if messagebox.askyesno("Resolve Doubt", "Are you sure you want to mark this doubt as Resolved?"):
            try:
                self.store.resolve_doubt(self.doubt_id)
                self.status_var.set("Status: Resolved")
                self.status_lbl.config(fg=style.COLOR_SUCCESS)
                if hasattr(self, "resolve_btn") and self.resolve_btn:
                    self.resolve_btn.pack_forget()
                messagebox.showinfo("Success", "Doubt has been marked as Resolved.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to resolve doubt: {e}")
