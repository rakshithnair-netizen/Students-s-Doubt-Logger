import tkinter as tk
from tkinter import messagebox
from . import style

class LoginFrame(tk.Frame):
    def __init__(self, parent, store, on_login_success):
        super().__init__(parent, bg=style.BG_MAIN)
        self.store = store
        self.on_login_success = on_login_success
        self.mode = "login"  # "login" or "signup"
        
        self.setup_ui()

    def setup_ui(self):
        # Clear any existing widgets
        for widget in self.winfo_children():
            widget.destroy()

        if self.mode == "login":
            self.setup_login_ui()
        else:
            self.setup_signup_ui()

    def setup_login_ui(self):
        # Card Container Frame
        card = tk.Frame(self, bg=style.BG_CARD, bd=1, relief="solid")
        card.place(relx=0.5, rely=0.5, anchor="center", width=350, height=330)

        # Title Labels
        tk.Label(
            card,
            text="Welcome Back",
            font=style.FONT_HEADING,
            bg=style.BG_CARD,
            fg=style.FG_DARK
        ).pack(pady=(20, 5))

        tk.Label(
            card,
            text="Please enter your credentials to login",
            font=style.FONT_BODY,
            bg=style.BG_CARD,
            fg=style.FG_MUTED
        ).pack(pady=(0, 15))

        # Username Input
        tk.Label(card, text="Username", font=style.FONT_LABEL, bg=style.BG_CARD, fg=style.FG_MUTED).pack(anchor="w", padx=30)
        self.user_e = tk.Entry(card, font=style.FONT_INPUT, bg=style.BG_INPUT, fg=style.FG_DARK, bd=1, relief="solid")
        self.user_e.pack(fill="x", padx=30, pady=(2, 10), ipady=4)
        self.user_e.focus()

        # Password Input
        tk.Label(card, text="Password", font=style.FONT_LABEL, bg=style.BG_CARD, fg=style.FG_MUTED).pack(anchor="w", padx=30)
        self.pass_e = tk.Entry(card, show="*", font=style.FONT_INPUT, bg=style.BG_INPUT, fg=style.FG_DARK, bd=1, relief="solid")
        self.pass_e.pack(fill="x", padx=30, pady=(2, 15), ipady=4)

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
        submit_btn.pack(fill="x", padx=30, ipady=5)

        # Switch to Signup link
        toggle_btn = tk.Button(
            card,
            text="Don't have an account? Sign Up",
            font=style.FONT_BODY,
            bg=style.BG_CARD,
            fg=style.COLOR_PRIMARY,
            activebackground=style.BG_CARD,
            activeforeground="#2563eb",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.toggle_mode
        )
        toggle_btn.pack(pady=(10, 0))

    def setup_signup_ui(self):
        # Card Container Frame
        card = tk.Frame(self, bg=style.BG_CARD, bd=1, relief="solid")
        card.place(relx=0.5, rely=0.5, anchor="center", width=350, height=370)

        # Title Labels
        tk.Label(
            card,
            text="Create Account",
            font=style.FONT_HEADING,
            bg=style.BG_CARD,
            fg=style.FG_DARK
        ).pack(pady=(15, 5))

        tk.Label(
            card,
            text="Register as a Student or Teacher",
            font=style.FONT_BODY,
            bg=style.BG_CARD,
            fg=style.FG_MUTED
        ).pack(pady=(0, 10))

        # Username Input
        tk.Label(card, text="Username", font=style.FONT_LABEL, bg=style.BG_CARD, fg=style.FG_MUTED).pack(anchor="w", padx=30)
        self.user_e = tk.Entry(card, font=style.FONT_INPUT, bg=style.BG_INPUT, fg=style.FG_DARK, bd=1, relief="solid")
        self.user_e.pack(fill="x", padx=30, pady=(2, 8), ipady=4)
        self.user_e.focus()

        # Password Input
        tk.Label(card, text="Password", font=style.FONT_LABEL, bg=style.BG_CARD, fg=style.FG_MUTED).pack(anchor="w", padx=30)
        self.pass_e = tk.Entry(card, show="*", font=style.FONT_INPUT, bg=style.BG_INPUT, fg=style.FG_DARK, bd=1, relief="solid")
        self.pass_e.pack(fill="x", padx=30, pady=(2, 8), ipady=4)

        # Role Input
        tk.Label(card, text="Role", font=style.FONT_LABEL, bg=style.BG_CARD, fg=style.FG_MUTED).pack(anchor="w", padx=30)
        self.role_var = tk.StringVar(value="student")
        role_frame = tk.Frame(card, bg=style.BG_CARD)
        role_frame.pack(fill="x", padx=30, pady=(2, 12))
        
        tk.Radiobutton(role_frame, text="Student", variable=self.role_var, value="student", bg=style.BG_CARD, activebackground=style.BG_CARD).pack(side="left", padx=(0, 20))
        tk.Radiobutton(role_frame, text="Teacher", variable=self.role_var, value="teacher", bg=style.BG_CARD, activebackground=style.BG_CARD).pack(side="left")

        # Submit button
        submit_btn = tk.Button(
            card,
            text="Sign Up",
            font=style.FONT_LABEL,
            bg=style.COLOR_SUCCESS,
            fg="white",
            activebackground="#059669",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            command=self.handle_signup
        )
        submit_btn.config(highlightbackground=style.BG_CARD)
        submit_btn.pack(fill="x", padx=30, ipady=5)

        # Switch to Login link
        toggle_btn = tk.Button(
            card,
            text="Already have an account? Sign In",
            font=style.FONT_BODY,
            bg=style.BG_CARD,
            fg=style.COLOR_PRIMARY,
            activebackground=style.BG_CARD,
            activeforeground="#2563eb",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.toggle_mode
        )
        toggle_btn.pack(pady=(10, 0))

    def toggle_mode(self):
        self.mode = "signup" if self.mode == "login" else "login"
        self.setup_ui()

    def handle_login(self, event=None):
        username = self.user_e.get().strip()
        password = self.pass_e.get().strip()

        role = self.store.authenticate(username, password)
        if role:
            self.on_login_success(username, role)
        else:
            messagebox.showerror("Error", "Invalid username or password.")

    def handle_signup(self):
        username = self.user_e.get().strip()
        password = self.pass_e.get().strip()
        role = self.role_var.get()

        if not username or not password:
            messagebox.showwarning("Warning", "Please enter both username and password.")
            return

        success = self.store.register_user(username, password, role)
        if success:
            messagebox.showinfo("Success", "Account created successfully! Please sign in.")
            self.mode = "login"
            self.setup_ui()
        else:
            messagebox.showerror("Error", "Username already exists. Please choose a different one.")
