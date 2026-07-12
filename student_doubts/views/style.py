import tkinter as tk
from tkinter import ttk

# ── Color Palette Constants ──
BG_MAIN = "#f1f5f9"       # Soft slate gray background
BG_CARD = "#ffffff"       # Clean card white background
BG_INPUT = "#f8fafc"      # Off-white background for input controls
FG_DARK = "#0f172a"       # Slate 900 for high-contrast text
FG_MUTED = "#475569"      # Slate 600 for labels & descriptions
FG_LIGHT = "#f8fafc"      # Near white for text on dark backgrounds
BORDER_COLOR = "#e2e8f0"  # Light gray divider border color

# Accent Colors
COLOR_PRIMARY = "#3b82f6"  # Blue (Submit/Sign In)
COLOR_SUCCESS = "#10b981"  # Emerald Green (Reply)
COLOR_DANGER = "#ef4444"   # Red (Logout/Urgent)

# Fonts
FONT_HEADING = ("Helvetica", 18, "bold")
FONT_TITLE = ("Helvetica", 12, "bold")
FONT_LABEL = ("Helvetica", 9, "bold")
FONT_BODY = ("Helvetica", 9)
FONT_INPUT = ("Helvetica", 10)


def apply_ttk_theme():
    """Configures centralized styling parameters for TTK widgets (Treeview)."""
    style = ttk.Style()
    style.theme_use("clam")
    
    # Configure Treeview styling
    style.configure(
        "Treeview", 
        background=BG_CARD, 
        foreground=FG_DARK, 
        rowheight=25, 
        fieldbackground=BG_CARD,
        font=FONT_BODY
    )
    
    style.configure(
        "Treeview.Heading", 
        background=BG_MAIN, 
        foreground=FG_MUTED, 
        font=FONT_LABEL, 
        relief="flat"
    )
    
    style.map(
        "Treeview.Heading", 
        background=[("active", BORDER_COLOR)]
    )
    
    style.map(
        "Treeview", 
        background=[("selected", "#dbeafe")], 
        foreground=[("selected", "#1e3a8a")]
    )
