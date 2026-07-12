import tkinter as tk
from tkinter import messagebox
from . import style

class LoginFrame(tk.Frame):
    def __init__(self, parent, store, on_login_success):
        super().__init__(parent, bg=style.BG_MAIN)
        self.store = store
        self.on_login_success = on_login_success
        
        self.setup_ui()

    def setup_ui(self):
        # Card Container Frame
        card = tk.Frame(self, bg=style.BG_CARD, bd=1, relief="solid")
        card.place(relx=0.5, rely=0.5, anchor="center", width=350, height=280)

        # Title Labels
        tk.Label(
            card,
            text="Welcome Back",
            font=style.FONT_HEADING,
            bg=style.BG_CARD,
            fg=style.FG_DARK
        ).pack(pady=(25, 5))

        tk.Label(
            card,
            text="Please enter your credentials to login",
            font=style.FONT_BODY,
            bg=style.BG_CARD,
            fg=style.FG_MUTED
        ).pack(pady=(0, 20))

        # Username Input
        tk.Label(card, text="Username", font=style.FONT_LABEL, bg=style.BG_CARD, fg=style.FG_MUTED).pack(anchor="w", padx=30)
        self.user_e = tk.Entry(card, font=style.FONT_INPUT, bg=style.BG_INPUT, fg=style.FG_DARK, bd=1, relief="solid")
        self.user_e.pack(fill="x", padx=30, pady=(2, 10), ipady=4)
        self.user_e.focus()

        # Password Input
        tk.Label(card, text="Password", font=style.FONT_LABEL, bg=style.BG_CARD, fg=style.FG_MUTED).pack(anchor="w", padx=30)
        self.pass_e = tk.Entry(card, show="*", font=style.FONT_INPUT, bg=style.BG_INPUT, fg=style.FG_DARK, bd=1, relief="solid")
        self.pass_e.pack(fill="x", padx=30, pady=(2, 20), ipady=4)

        # Event bindings
        self.user_e.bind("<Return>", self.handle_login)
        self.pass_e.bind("<Return>", self.handle_login)

        # Submit button
        submit_btn = tk.Button(
            card,
            text="Sign In",
            font=style.FONT_LABEL,
            bg=style.COLOR_PRIMARY,
            fg="white",
            activebackground="#2563eb",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            command=self.handle_login
        )
        submit_btn.config(highlightbackground=style.BG_CARD)
        submit_btn.pack(fill="x", padx=30, ipady=6)

    def handle_login(self, event=None):
        username = self.user_e.get().strip()
        password = self.pass_e.get().strip()

        role = self.store.authenticate(username, password)
        if role:
            self.on_login_success(username, role)
        else:
            messagebox.showerror("Error", "Invalid username or password.")
