import tkinter as tk
from tkinter import ttk, messagebox
from . import style
from .chat import ChatFrame

class TeacherDashboardFrame(tk.Frame):
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
        # LEFT PANE: All Student Doubts list
        # ──────────────────────────────────────────────────────────
        left_frame = tk.LabelFrame(
            main_container,
            text="All Student Doubts",
            font=style.FONT_TITLE,
            bg=style.BG_CARD,
            fg=style.FG_DARK,
            padx=10,
            pady=10,
            bd=1,
            relief="solid"
        )
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.left_frame = left_frame

        tree_container = tk.Frame(left_frame, bg=style.BG_CARD)
        tree_container.pack(fill="both", expand=True)
        self.tree_container = tree_container

        cols = ("ID", "Student", "Subject", "Teacher", "Severity", "Urgent", "Needs Explanation", "Description", "Reply")
        self.tree = ttk.Treeview(tree_container, columns=cols, show="headings")

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        col_widths = {
            "ID": 40,
            "Student": 80,
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

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Double-1>", self.on_double_click)

        # ──────────────────────────────────────────────────────────
        # RIGHT PANE: Selected Doubt details & reply card
        # ──────────────────────────────────────────────────────────
        right_frame = tk.LabelFrame(
            main_container,
            text="Doubt details & Reply",
            font=style.FONT_TITLE,
            bg=style.BG_CARD,
            fg=style.FG_DARK,
            padx=15,
            pady=10,
            bd=1,
            relief="solid",
            width=350
        )
        right_frame.pack(side="right", fill="both")
        right_frame.pack_propagate(False)
        self.right_frame = right_frame

        # Detail UI StringVars
        self.lbl_student = tk.StringVar(value="-")
        self.lbl_subject = tk.StringVar(value="-")
        self.lbl_severity = tk.StringVar(value="-")
        self.lbl_flags = tk.StringVar(value="-")

        details_panel = tk.Frame(right_frame, bg=style.BG_CARD)
        details_panel.pack(fill="x", pady=(5, 10))

        def create_detail_row(parent, label_text, var):
            row = tk.Frame(parent, bg=style.BG_CARD)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=label_text, font=style.FONT_LABEL, bg=style.BG_CARD, fg=style.FG_MUTED, width=12, anchor="w").pack(side="left")
            tk.Label(row, textvariable=var, font=style.FONT_BODY, bg=style.BG_CARD, fg=style.FG_DARK, anchor="w").pack(side="left", fill="x", expand=True)

        create_detail_row(details_panel, "Student:", self.lbl_student)
        create_detail_row(details_panel, "Subject:", self.lbl_subject)
        create_detail_row(details_panel, "Severity:", self.lbl_severity)
        create_detail_row(details_panel, "Flags:", self.lbl_flags)

        # Description view panel
        tk.Label(right_frame, text="Description:", font=style.FONT_LABEL, bg=style.BG_CARD, fg=style.FG_MUTED).pack(anchor="w", pady=(5, 2))
        self.desc_viewer = tk.Text(right_frame, height=5, font=style.FONT_BODY, bg=style.BG_INPUT, fg=style.FG_DARK, bd=1, relief="solid", state="disabled", wrap="word")
        self.desc_viewer.pack(fill="x", pady=(0, 10))

        # Reply input field
        tk.Label(right_frame, text="Your Reply:", font=style.FONT_LABEL, bg=style.BG_CARD, fg=style.FG_MUTED).pack(anchor="w", pady=(5, 2))
        self.reply_e = tk.Text(right_frame, height=4, font=style.FONT_INPUT, bg=style.BG_CARD, fg=style.FG_DARK, bd=1, relief="solid", wrap="word")
        self.reply_e.pack(fill="x", pady=(0, 15))

        self.selected_doubt_id = None

        # Submit reply button
        reply_btn = tk.Button(
            right_frame,
            text="Submit Reply",
            font=style.FONT_LABEL,
            bg=style.COLOR_SUCCESS,
            fg="white",
            activebackground="#059669",
            relief="flat",
            cursor="hand2",
            command=self.send_reply
        )
        reply_btn.config(highlightbackground=style.BG_CARD)
        reply_btn.pack(fill="x", ipady=5)

        self.pane_resolve_btn = tk.Button(
            right_frame,
            text="Mark as Resolved",
            font=style.FONT_LABEL,
            bg=style.COLOR_PRIMARY,
            fg="white",
            activebackground="#2563eb",
            relief="flat",
            cursor="hand2",
            command=self.resolve_selected_doubt
        )
        self.pane_resolve_btn.config(highlightbackground=style.BG_CARD)
        self.pane_resolve_btn.pack(fill="x", ipady=5, pady=(10, 0))

        self.load_list()

    def load_list(self):
        self.tree.delete(*self.tree.get_children())
        for d in self.store.get_all_doubts():
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

            self.tree.insert("", "end", iid=str(d["id"]), values=(
                d["id"],
                d["student"],
                d["subject"],
                d.get("teacher", ""),
                sev_display,
                urgent_display,
                explain_display,
                d["desc"],
                reply_display
            ))

    def on_tree_select(self, event):
        sel = self.tree.selection()
        if not sel:
            self.clear_details()
            return

        did = int(sel[0])
        self.selected_doubt_id = did

        # Find matching doubt
        doubt = next((d for d in self.store.get_all_doubts() if d["id"] == did), None)
        if doubt:
            self.lbl_student.set(doubt["student"])
            self.lbl_subject.set(doubt["subject"])
            self.lbl_severity.set(doubt["severity"])
            
            flags = []
            if doubt.get("urgent") == "Yes":
                flags.append("Urgent")
            if doubt.get("explain") == "Yes":
                flags.append("Explain")
            self.lbl_flags.set(", ".join(flags) if flags else "None")

            # Enable description text viewer to update it
            self.desc_viewer.config(state="normal")
            self.desc_viewer.delete("1.0", "end")
            self.desc_viewer.insert("1.0", doubt["desc"])
            self.desc_viewer.config(state="disabled")

            if doubt.get("status") == "Resolved":
                self.pane_resolve_btn.config(state="disabled")
            else:
                self.pane_resolve_btn.config(state="normal")

            # Load reply
            self.reply_e.delete("1.0", "end")
            self.reply_e.insert("1.0", doubt["reply"])

    def clear_details(self):
        self.selected_doubt_id = None
        self.lbl_student.set("-")
        self.lbl_subject.set("-")
        self.lbl_severity.set("-")
        self.lbl_flags.set("-")
        
        self.desc_viewer.config(state="normal")
        self.desc_viewer.delete("1.0", "end")
        self.desc_viewer.config(state="disabled")
        
        self.reply_e.delete("1.0", "end")

    def send_reply(self):
        did = self.selected_doubt_id
        if did is None:
            messagebox.showwarning("Warning", "Please select a doubt from the table to reply.")
            return

        txt = self.reply_e.get("1.0", "end").strip()
        if not txt:
            messagebox.showwarning("Warning", "Please write a reply before submitting.")
            return

        success = self.store.submit_reply(did, txt)
        if success:
            self.clear_details()
            self.load_list()
            messagebox.showinfo("Success", "Reply updated successfully!")
        else:
            messagebox.showerror("Error", "Could not submit reply.")

    def on_double_click(self, event):
        if hasattr(self, "chat_frame") and self.chat_frame:
            return

        item = self.tree.selection()
        if not item:
            return
        
        values = self.tree.item(item[0], "values")
        if not values:
            return
        
        reply = values[8]
        if reply == "⌛ Pending":
            messagebox.showinfo("Chat Not Available", "You can start chatting once you reply to the student's doubt.")
            return
        
        try:
            doubt_id = int(values[0])
        except (ValueError, TypeError):
            return
        
        # Hide the treeview container and details pane
        self.tree_container.pack_forget()
        self.right_frame.pack_forget()
        
        # Create and pack the ChatFrame
        self.chat_frame = ChatFrame(
            self.left_frame,
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
        
        # Restore right details pane, treeview container, and refresh list
        self.right_frame.pack(side="right", fill="both")
        self.tree_container.pack(fill="both", expand=True)
        self.load_list()

    def resolve_selected_doubt(self):
        did = self.selected_doubt_id
        if did is None:
            messagebox.showwarning("Warning", "Please select a doubt to resolve.")
            return
        if messagebox.askyesno("Resolve Doubt", "Are you sure you want to mark this doubt as Resolved?"):
            self.store.resolve_doubt(did)
            self.clear_details()
            self.load_list()
            messagebox.showinfo("Success", "Doubt marked as Resolved.")
            
