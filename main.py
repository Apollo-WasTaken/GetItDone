import customtkinter as ctk
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable

# Detect if running as executable or from source
# When frozen (exe), use exe directory, otherwise use script directory
if getattr(sys, "frozen", False):
    APP_DIR = Path(sys.executable).parent
else:
    APP_DIR = Path(__file__).parent

TASKS_FILE = APP_DIR / "tasks.json"
ctk.set_appearance_mode("dark")  # Default to dark mode, can be toggled
ctk.set_default_color_theme("blue")


def ensure_tasks_file():
    #  Create tasks.json with empty array if it doesn't exist
    if not TASKS_FILE.exists():
        TASKS_FILE.write_text("[]", encoding="utf-8")


# ─────────────────────────────────────────────────────────────
# DESIGN TOKENS

class T:
    BG_PRIMARY = ("#F8F7F4", "#1E1E1C")
    BG_PAGE = ("#F0EFE9", "#141413")

    TEXT_PRIMARY = ("#1A1A1A", "#FAF9F5")

    BORDER_TERTIARY = ("#E0DED5", "#2E2E2B")
    BORDER_SECONDARY = ("#D0CEC3", "#3D3D3A")
    BORDER_PRIMARY = ("#C0BEB1", "#4D4D49")

    ACCENT_CORAL = ("#D97757", "#D4714A")
    ACCENT_CORAL_HOV = ("#C06345", "#C06038")
    ACCENT_CORAL_TXT = ("#FFFFFF", "#FFFFFF")

    FONT_SANS = "Inter"

    FS_HEADING = 30
    FS_BODY = 16

    RADIUS_MD = 24
    RADIUS_LG = 28
    RADIUS_BUTTONS = 14
    HEIGHT_MD = 44
    HEIGHT_SM = 32

    BORDER_WIDTH = 1


# ─────────────────────────────────────────────────────────────
# TASK WIDGET
# Custom component for displaying a single task with Edit/Delete buttons

class TaskWidget(ctk.CTkFrame):
    def __init__(self, parent, task_text: str, task_index: int, on_edit: Callable, on_delete: Callable):

        super().__init__(parent, fg_color="transparent")
        self.task_text = task_text
        self.task_index = task_index
        self.on_edit = on_edit
        self.on_delete = on_delete
        
        self.grid_columnconfigure(0, weight=1)
        
        # Task label
        self.label = ctk.CTkLabel(
            self,
            text=task_text,
            font=(T.FONT_SANS, T.FS_BODY),
            text_color=T.TEXT_PRIMARY,
            anchor="w"
        )
        self.label.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        # Button frame
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=0, column=1, sticky="e")
        
        # Edit button
        self.edit_button = ctk.CTkButton(
            self.button_frame,
            text="Edit",
            width=60,
            height=T.HEIGHT_SM,
            font=(T.FONT_SANS, 12),
            fg_color=T.BORDER_SECONDARY[1],
            hover_color=T.BORDER_PRIMARY[1],
            text_color=T.TEXT_PRIMARY,
            corner_radius=8,
            command=lambda: self.on_edit(self.task_index)
        )
        self.edit_button.grid(row=0, column=0, padx=(0, 5))
        
        # Delete button
        self.delete_button = ctk.CTkButton(
            self.button_frame,
            text="Delete",
            width=60,
            height=T.HEIGHT_SM,
            font=(T.FONT_SANS, 12),
            fg_color=T.ACCENT_CORAL,
            hover_color=T.ACCENT_CORAL_HOV,
            text_color=T.ACCENT_CORAL_TXT,
            corner_radius=8,
            command=lambda: self.on_delete(self.task_index)
        )
        self.delete_button.grid(row=0, column=1)
    
    def update_text(self, new_text: str):
        self.task_text = new_text
        self.label.configure(text=new_text)


# ─────────────────────────────────────────────────────────────
# APP

class App(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("Task Manager")
        self.minsize(1200, 800)
        
        # Set window icon (works for both source and exe)
        icon_path = APP_DIR / "get_it_done_logo.ico"
        if icon_path.exists():
            self.iconbitmap(str(icon_path))
        
        self.configure(fg_color=T.BG_PAGE)
        # Center content in window
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.tasks = []
        self.create_layout()
        self.load_tasks()
        self.after(0, self._show_maximized)
    
    # ── JSON / task data (helpers) ─────────────────────────────

    def _normalize_task(self, item):
        #  Turn one JSON item into {"text", "created_at"}
        if isinstance(item, str):
            return {
                "text": item,
                "created_at": datetime.now().isoformat(),
            }
        if isinstance(item, dict) and "text" in item:
            return item
        return None

    def _format_task_display(self, task):
        text = task["text"]
        try:
            when = datetime.fromisoformat(task["created_at"])
            time_str = when.strftime("%d.%m.%Y %H:%M")  # ← customize this line
        except (KeyError, ValueError):
            time_str = ""
        if time_str:
            return f"{text}  ·  {time_str}"
        return text

    def load_tasks(self):
        ensure_tasks_file()
        try:
            with open(TASKS_FILE, encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []

        if not isinstance(data, list):
            data = []

        self.tasks = []
        for item in data:
            task = self._normalize_task(item)
            if task is None:
                continue
            self.tasks.append(task)
            self._add_task_widget(task, len(self.tasks) - 1)

    def save_tasks(self):
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, indent=4, ensure_ascii=False)

    def _add_task_widget(self, task, index):
        display_text = self._format_task_display(task)
        widget = TaskWidget(
            self.scrollable_frame,
            display_text,
            index,
            on_edit=self.edit_task,
            on_delete=self.delete_task
        )
        widget.grid(row=index, column=0, sticky="ew", pady=(0, 15))
        self.task_widgets.append(widget)

    def _show_maximized(self):
        self.state("zoomed")  # fill the screen on Windows

    # ---------------------------------------------------------
    # LAYOUT
    # ---------------------------------------------------------
    def create_layout(self):

        # Center container
        self.center_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.center_frame.grid(
            row=0,
            column=0
        )

        # Main card
        self.task_card = ctk.CTkFrame(
            self.center_frame,
            width=650,
            height=550,
            fg_color=T.BG_PRIMARY,
            corner_radius=T.RADIUS_LG,
            border_width=T.BORDER_WIDTH,
            border_color=T.BORDER_TERTIARY
        )

        self.task_card.grid(row=0, column=0)
        self.task_card.grid_propagate(False)

        # Card layout
        self.task_card.grid_columnconfigure(0, weight=1)
        self.task_card.grid_rowconfigure(3, weight=1)

        self.create_heading()
        self.create_entry()
        self.create_buttons()
        
        self.create_scrollable_task_list()
        self.create_theme_toggle()

    # ---------------------------------------------------------
    # HEADING
    # ---------------------------------------------------------
    def create_heading(self):

        self.heading = ctk.CTkLabel(
            self.task_card,
            text="Get it done",
            font=(T.FONT_SANS, T.FS_HEADING, "bold"),
            text_color=T.TEXT_PRIMARY
        )

        self.heading.grid(
            row=0,
            column=0,
            sticky="n",
            padx=30,
            pady=(30, 20)
        )

    # ---------------------------------------------------------
    # ENTRY
    # ---------------------------------------------------------
    def create_entry(self):

        self.task_entry = ctk.CTkEntry(
            self.task_card,
            placeholder_text="Add a task.....",
            font=(T.FONT_SANS, T.FS_BODY),
            height=T.HEIGHT_MD,
            fg_color=T.BG_PRIMARY,
            border_color=T.BORDER_SECONDARY,
            border_width=T.BORDER_WIDTH,
            corner_radius=T.RADIUS_MD
        )

        self.task_entry.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=30,
            pady=(0, 20)
        )

        def focus_in(event):
            self.task_entry.configure(
                border_color=T.BORDER_PRIMARY
            )

        def focus_out(event):
            self.task_entry.configure(
                border_color=T.BORDER_SECONDARY
            )

        self.task_entry.bind("<FocusIn>", focus_in)
        self.task_entry.bind("<FocusOut>", focus_out)
        self.task_entry.bind("<Return>", lambda event: self.add_task())
    # ---------------------------------------------------------
    # BUTTONS
    # ---------------------------------------------------------
    def create_buttons(self):

        self.button_frame = ctk.CTkFrame(
            self.task_card,
            fg_color="transparent"
        )

        self.button_frame.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=30,
            pady=(0, 20)
        )

        self.button_frame.grid_columnconfigure(0, weight=1)

        self.add_button = ctk.CTkButton(
            self.button_frame,
            font= (T.FONT_SANS, T.FS_BODY),
            text="Add Task",
            command=self.add_task,
            fg_color=T.ACCENT_CORAL,
            hover_color=T.ACCENT_CORAL_HOV,
            text_color=T.ACCENT_CORAL_TXT,
            height=T.HEIGHT_MD,
            corner_radius=T.RADIUS_BUTTONS
        )
        
        self.add_button.grid(
            row=0,
            column=0,
            sticky="ew"
        )

    # ---------------------------------------------------------
    # SCROLLABLE TASK LIST
    # ---------------------------------------------------------
    def create_scrollable_task_list(self):
        self.task_widgets = []
        
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self.task_card,
            fg_color="transparent",
            label_text=""
        )
        
        self.scrollable_frame.grid(
            row=3,
            column=0,
            sticky="nsew",
            padx=30,
            pady=(0, 30)
        )

    def create_theme_toggle(self):
        self.theme_button = ctk.CTkButton(
            self.task_card,
            text="🌙",
            width=50,
            height=50,
            font=(T.FONT_SANS, 18),
            fg_color=T.BORDER_SECONDARY[1],
            hover_color=T.BORDER_PRIMARY[1],
            text_color=T.TEXT_PRIMARY,
            corner_radius=20,
            command=self.toggle_appearance_mode
        )
        self.theme_button.grid(
            row=3,
            column=0,
            sticky="sw",
            padx=20,
            pady=20
        )

    def toggle_appearance_mode(self):
        current_mode = ctk.get_appearance_mode()
        new_mode = "Light" if current_mode == "Dark" else "Dark"
        ctk.set_appearance_mode(new_mode)
        
        # Update button text
        self.theme_button.configure(text="☀️" if new_mode == "Light" else "🌙")

    def add_task(self):
        
        text = self.task_entry.get().strip()

        if not text:
            return
        task = {
            "text": text,
            "created_at": datetime.now().isoformat(),
        }
        self.tasks.append(task)
        self._add_task_widget(task, len(self.tasks) - 1)
       
        self.task_entry.delete(0, "end")
        self.save_tasks()

    def delete_task(self, index):
        if index < 0 or index >= len(self.tasks):
            return

        del self.tasks[index]
        self.task_widgets[index].destroy()
        del self.task_widgets[index]
        
        # Re-index remaining widgets
        for i, widget in enumerate(self.task_widgets):
            widget.task_index = i
            widget.grid(row=i, column=0, sticky="ew", pady=(0, 10))
        
        self.save_tasks()

    def edit_task(self, index):
        if index < 0 or index >= len(self.tasks):
            return

        task = self.tasks[index]
        current_text = task["text"]

        # Create edit dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Task")
        dialog.geometry("400x200")
        dialog.configure(fg_color=T.BG_PAGE)
        
        # Center the dialog
        dialog.transient(self)
        dialog.grab_set()
        
        dialog.grid_columnconfigure(0, weight=1)
        dialog.grid_rowconfigure(0, weight=1)
        
        # Dialog frame
        dialog_frame = ctk.CTkFrame(
            dialog,
            fg_color=T.BG_PRIMARY,
            corner_radius=T.RADIUS_LG,
            border_width=T.BORDER_WIDTH,
            border_color=T.BORDER_TERTIARY
        )
        dialog_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        dialog_frame.grid_columnconfigure(0, weight=1)
        
        # Entry
        entry = ctk.CTkEntry(
            dialog_frame,
            font=(T.FONT_SANS, T.FS_BODY),
            height=T.HEIGHT_MD,
            fg_color=T.BG_PRIMARY,
            border_color=T.BORDER_SECONDARY,
            border_width=T.BORDER_WIDTH,
            corner_radius=T.RADIUS_MD
        )
        entry.insert(0, current_text)
        entry.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        entry.focus()
        entry.select_range(0, "end")
        
        # Button frame
        button_frame = ctk.CTkFrame(dialog_frame, fg_color="transparent")
        button_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        def save_edit():
            new_text = entry.get().strip()
            if new_text:
                task["text"] = new_text
                self.task_widgets[index].update_text(self._format_task_display(task))
                self.save_tasks()
            dialog.destroy()
        
        def cancel_edit():
            dialog.destroy()
        
        # Save button
        save_button = ctk.CTkButton(
            button_frame,
            text="Save",
            font=(T.FONT_SANS, T.FS_BODY),
            command=save_edit,
            fg_color=T.ACCENT_CORAL,
            hover_color=T.ACCENT_CORAL_HOV,
            text_color=T.ACCENT_CORAL_TXT,
            height=T.HEIGHT_MD,
            corner_radius=T.RADIUS_BUTTONS
        )
        save_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        # Cancel button
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            font=(T.FONT_SANS, T.FS_BODY),
            command=cancel_edit,
            fg_color=T.BORDER_SECONDARY[1],
            hover_color=T.BORDER_PRIMARY[1],
            text_color=T.TEXT_PRIMARY,
            height=T.HEIGHT_MD,
            corner_radius=T.RADIUS_BUTTONS
        )
        cancel_button.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
        # Bind Enter key to save
        entry.bind("<Return>", lambda event: save_edit())
        entry.bind("<Escape>", lambda event: cancel_edit())

if __name__ == "__main__":
    app = App()
    app.mainloop()
