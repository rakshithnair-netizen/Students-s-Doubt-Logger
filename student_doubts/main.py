import tkinter as tk
from models import DoubtStore
from views import style
from views.login import LoginFrame
from views.student import StudentDashboardFrame
from views.teacher import TeacherDashboardFrame
from views.admin import AdminDashboardFrame

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Doubt Management System")
        self.geometry("450x380")
        self.configure(bg=style.BG_MAIN)
        
        # Configure TTK Styles (Treeview)
        style.apply_ttk_theme()

        # Shared data store instance
        self.store = DoubtStore()
        
        # Header frame placeholder
        self.header_frame = None
        
        # Main content frame container
        self.container = tk.Frame(self, bg=style.BG_MAIN)
        self.container.pack(fill="both", expand=True)

        self.current_frame = None
        self.show_login_screen()

    def clear_current_frame(self):
        """Destroys current active view components."""
        if self.current_frame:
            self.current_frame.destroy()
            self.current_frame = None
        if self.header_frame:
            self.header_frame.destroy()
            self.header_frame = None

    def show_login_screen(self):
        self.clear_current_frame()
        
        # Set small screen for login
        self.geometry("450x380")
        
        self.current_frame = LoginFrame(
            self.container, 
            self.store, 
            on_login_success=self.on_login_success
        )
        self.current_frame.pack(fill="both", expand=True)

    def on_login_success(self, username, role):
        if role == "student":
            self.show_student_dashboard(username)
        elif role == "teacher":
            self.show_teacher_dashboard(username)
        elif role == "admin":
            self.show_admin_dashboard(username)

    def show_header(self, title):
        """Loads header frame with custom title and logout button."""
        self.header_frame = tk.Frame(self, bg=style.FG_DARK, height=50)
        self.header_frame.pack(fill="x", side="top")
        self.header_frame.pack_propagate(False)

        tk.Label(
            self.header_frame,
            text=title,
            font=style.FONT_TITLE,
            bg=style.FG_DARK,
            fg=style.FG_LIGHT
        ).pack(side="left", padx=15, pady=12)

        logout_btn = tk.Button(
            self.header_frame,
            text="Logout",
            font=style.FONT_LABEL,
            bg=style.COLOR_DANGER,
            fg="white",
            activebackground="#dc2626",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            command=self.show_login_screen
        )
        logout_btn.config(highlightbackground=style.FG_DARK)
        logout_btn.pack(side="right", padx=15, pady=10)

    def show_student_dashboard(self, username):
        self.clear_current_frame()
        
        # Set large dual-pane screen for dashboards
        self.geometry("1000x600")
        
        self.show_header(f"Student Portal | Logged in as: {username}")
        
        self.current_frame = StudentDashboardFrame(self.container, self.store, username)
        self.current_frame.pack(fill="both", expand=True)

    def show_teacher_dashboard(self, username):
        self.clear_current_frame()
        
        # Set large dual-pane screen for dashboards
        self.geometry("1050x600")
        
        self.show_header(f"Teacher Portal | Logged in as: {username}")
        
        self.current_frame = TeacherDashboardFrame(self.container, self.store, username)
        self.current_frame.pack(fill="both", expand=True)

    def show_admin_dashboard(self, username):
        self.clear_current_frame()
        self.geometry("1120x680")
        self.show_header(f"Administration Portal | Logged in as: {username}")
        self.current_frame = AdminDashboardFrame(self.container, self.store, username)
        self.current_frame.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = App()
    app.mainloop()
