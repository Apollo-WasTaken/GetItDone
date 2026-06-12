import customtkinter as ctk
import json
import sys
import os
import ctypes
from pathlib import Path
from datetime import datetime
from typing import Callable

# Detect if running as executable or from source
if getattr(sys, "frozen", False):
    APP_DIR = Path(sys.executable).parent
else:
    APP_DIR = Path(__file__).parent

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

# Load and register Anthropic Sans fonts
def load_custom_fonts():
    fonts_to_load = [
        "AnthropicSans-Display-Bold-Static.otf",
        "AnthropicSans-Display-Regular-Static.otf",
        "AnthropicSans-Display-Medium-Static.otf",
        "AnthropicSans-Display-Semibold-Static.otf",
        "AnthropicSans-Display-Extrabold-Static.otf",
    ]
    for font_file in fonts_to_load:
        font_path = resource_path(os.path.join("Anthropic Sans-fontiko", font_file))
        if sys.platform == "win32" and os.path.exists(font_path):
            try:
                # 0x10 is FR_PRIVATE (registers font only for this process)
                ctypes.windll.gdi32.AddFontResourceExW(font_path, 0x10, 0)
            except Exception as e:
                print(f"Error loading custom font {font_file}: {e}")

load_custom_fonts()

TASKS_FILE = APP_DIR / "tasks.json"

def ensure_tasks_file():
    #  Create tasks.json with empty array if it doesn't exist
    if not TASKS_FILE.exists():
        TASKS_FILE.write_text("[]", encoding="utf-8")

# Theme definitions
# Main Surfaces
root_bg             = "#0C0E22"
content_card_bg     = "#0F1028"
content_card_border = "#252560"

# Inner Cards / Task Cards
task_card_bg        = "#14143A"
task_card_hover     = "#1A1A48"
task_card_selected  = "#221F5A"
task_card_border    = "#252560"

# Text
text_primary        = "#EAE8F6"
text_secondary      = "#B8B1E8"
text_placeholder    = "#9488CC"

# Primary Button
button_primary_bg      = "#6448E4"
button_primary_hover   = "#7860F8"
button_primary_border  = "#2E2A78"
button_primary_text    = "#FFFFFF"

# Secondary Button
button_secondary_bg      = "#14143A"
button_secondary_hover   = "#1A1A48"
button_secondary_border  = "#252560"
button_secondary_text    = "#EAE8F6"

# General Tokens
BG_MAIN      = "#0C0E22"
BG_CARD      = "#0F1028"
BG_WIDGET    = "#161840"
BORDER       = "#252560"
TEXT         = "#EAE8F6"
TEXT_MUTED   = "#9488CC"
ACCENT       = "#6448E4"
ACCENT_HOVER = "#7860F8"

# Layout Constants
RADIUS_MD = 24
RADIUS_LG = 28
RADIUS_BUTTONS = 8
HEIGHT_MD = 44
HEIGHT_SM = 32
BORDER_WIDTH = 1
# Task widget: displays a single task with edit/delete actions

class TaskWidget(ctk.CTkFrame):
    def __init__(self, parent, task_text: str, task_index: int, on_edit: Callable, on_delete: Callable):
        super().__init__(
            parent,
            fg_color=task_card_bg,
            border_color=task_card_border,
            border_width=BORDER_WIDTH,
            corner_radius=12
        )
        self.task_text = task_text
        self.task_index = task_index
        self.on_edit = on_edit
        self.on_delete = on_delete
        
        self.grid_columnconfigure(0, weight=1)
        
        app = self.winfo_toplevel()
        
        # Label showing task text; wrap to avoid overflow
        self.label = ctk.CTkLabel(
            self,
            text=task_text,
            font=app.FONT_LABEL,
            text_color=text_primary,
            anchor="w",
            wraplength=560
        )
        self.label.grid(row=0, column=0, sticky="ew", padx=(15, 5), pady=10)
        
        # Container for edit/delete buttons
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=0, column=1, sticky="e", padx=(0, 5), pady=10)
        
        # Edit button, opens edit 
        self.edit_button = ctk.CTkButton(
            self.button_frame,
            text="Edit",
            width=80,
            height=HEIGHT_SM,
            font=app.FONT_BUTTON,
            fg_color=button_secondary_bg,
            hover_color=button_secondary_hover,
            border_color=button_secondary_border,
            border_width=1,
            text_color=button_secondary_text,
            corner_radius=8,
            command=lambda: self.on_edit(self.task_index)
        )
        self.edit_button.grid(row=0, column=0, padx=(0, 5))
        
        # Delete button, removes task
        self.delete_button = ctk.CTkButton(
            self.button_frame,
            text="Delete",
            width=80,
            height=HEIGHT_SM,
            font=app.FONT_BUTTON,
            fg_color=button_primary_bg,
            hover_color=button_primary_hover,
            border_color=button_primary_border,
            border_width=1,
            text_color=button_primary_text,
            corner_radius=8,
            command=lambda: self.on_delete(self.task_index)
        )
        self.delete_button.grid(row=0, column=1)

        # Hover state change
        def on_enter(event):
            self.configure(fg_color=task_card_hover)
        def on_leave(event):
            self.configure(fg_color=task_card_bg)

        self.bind("<Enter>", on_enter)
        self.bind("<Leave>", on_leave)
        self.label.bind("<Enter>", on_enter)
        self.label.bind("<Leave>", on_leave)
    
    def update_text(self, new_text: str):
        self.task_text = new_text
        self.label.configure(text=new_text)


# Application class definition
class App(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("GetItDone")
        self.geometry("800x600")
        
        # Define custom fonts for titles, labels, buttons, entries
        self.FONT_TITLE = ("Anthropic Sans Display", 24, "bold")
        self.FONT_LABEL = ("Anthropic Sans Display", 16,"bold")

        self.FONT_BUTTON = ("Anthropic Sans Display", 20, "bold")
        self.FONT_ENTRY = ("Anthropic Sans Display", 18,"bold")
        
        # Set window icon (works for both source and exe)
        icon_path = APP_DIR / "get_it_done_logo.ico"
        if icon_path.exists():
            self.iconbitmap(str(icon_path))
        
        self.configure(fg_color=root_bg)
        # Center main UI components using grid weight
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.tasks = []
        self.create_layout()
        self.load_tasks()
    
# JSON helpers
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
            time_str = when.strftime("%d.%m.%Y %H:%M")
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

# Layout
    def create_layout(self):

        # Center container holds heading and task card
        self.center_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.center_frame.grid(
            row=0,
            column=0
        )

        self.heading = ctk.CTkLabel(
            self.center_frame,
            text="Get it done",
            font=self.FONT_TITLE,
            text_color=text_primary
        )

        self.heading.grid(
            row=0,
            column=0,
            sticky="n",
            padx=30,
            pady=(15, 10)
        )

        # Main card: contains entry, buttons, and scrollable task list
        self.task_card = ctk.CTkFrame(
            self.center_frame,
            width=620,
            height=440,
            fg_color=content_card_bg,
            corner_radius=RADIUS_LG,
            border_width=BORDER_WIDTH,
            border_color=content_card_border
        )

        self.task_card.grid(row=1, column=0, pady=(0, 15))
        self.task_card.grid_propagate(False)

        # Card layout
        self.task_card.grid_columnconfigure(0, weight=1)
        self.task_card.grid_rowconfigure(2, weight=1)

        self.create_entry()
        self.create_buttons()
        self.create_scrollable_task_list()

# Entry field for adding new tasks
    def create_entry(self):

        self.task_entry = ctk.CTkEntry(
            self.task_card,
            placeholder_text="Add a task.....",
            font=self.FONT_ENTRY,
            height=HEIGHT_MD,
            fg_color=BG_WIDGET,
            border_color=BORDER,
            border_width=BORDER_WIDTH,
            text_color=text_primary,
            placeholder_text_color=text_placeholder,
            corner_radius=RADIUS_MD
            
        )

        self.task_entry.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=30,
            pady=(20, 15)
        )

        def focus_in(event):
            self.task_entry.configure(
                border_color=ACCENT_HOVER
            )

        def focus_out(event):
            self.task_entry.configure(
                border_color=BORDER
            )

        self.task_entry.bind("<FocusIn>", focus_in)
        self.task_entry.bind("<FocusOut>", focus_out)
        self.task_entry.bind("<Return>", lambda event: self.add_task())

# Button panel containing Add Task button
    def create_buttons(self):

        self.button_frame = ctk.CTkFrame(
            self.task_card,
            fg_color="transparent"
        )

        self.button_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=30,
            pady=(0, 15)
        )

        self.button_frame.grid_columnconfigure(0, weight=1)

        self.add_button = ctk.CTkButton(
            self.button_frame,
            font=self.FONT_BUTTON,
            text="Add Task",
            command=self.add_task,
            fg_color=button_primary_bg,
            hover_color=button_primary_hover,
            border_color=button_primary_border,
            border_width=1,
            text_color=button_primary_text,
            height=HEIGHT_MD,
            corner_radius=RADIUS_BUTTONS
        )
        
        self.add_button.grid(
            row=0,
            column=0,
            sticky="ew"
        )

# Scrollable frame for task widgets
    def create_scrollable_task_list(self):
        self.task_widgets = []
        
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self.task_card,
            fg_color="transparent",
            label_text="",
            scrollbar_button_color=task_card_bg,
            scrollbar_button_hover_color=task_card_hover
        )
        
        self.scrollable_frame.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=30,
            pady=(0, 20)
        )
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

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

    # Remove task and update UI indices
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

    # Edit task via dialog
    def edit_task(self, index):
        if index < 0 or index >= len(self.tasks):
            return

        task = self.tasks[index]
        current_text = task["text"]

        # Create edit dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Task")
        dialog.geometry("400x200")
        dialog.configure(fg_color=root_bg)
        
        # Center the dialog
        dialog.transient(self)
        dialog.grab_set()
        
        dialog.grid_columnconfigure(0, weight=1)
        dialog.grid_rowconfigure(0, weight=1)
        
        # Dialog frame
        dialog_frame = ctk.CTkFrame(
            dialog,
            fg_color=content_card_bg,
            corner_radius=RADIUS_LG,
            border_width=BORDER_WIDTH,
            border_color=content_card_border
        )
        dialog_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        dialog_frame.grid_columnconfigure(0, weight=1)
        
        # Entry
        entry = ctk.CTkEntry(
            dialog_frame,
            font=self.FONT_ENTRY,
            height=HEIGHT_MD,
            fg_color=BG_WIDGET,
            border_color=BORDER,
            border_width=BORDER_WIDTH,
            text_color=text_primary,
            placeholder_text_color=text_placeholder,
            corner_radius=RADIUS_MD
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
            font=self.FONT_BUTTON,
            command=save_edit,
            fg_color=button_primary_bg,
            hover_color=button_primary_hover,
            border_color=button_primary_border,
            border_width=1,
            text_color=button_primary_text,
            height=HEIGHT_MD,
            corner_radius=RADIUS_BUTTONS
        )
        save_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        # Cancel button
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            font=self.FONT_BUTTON,
            command=cancel_edit,
            fg_color=button_secondary_bg,
            hover_color=button_secondary_hover,
            border_color=button_secondary_border,
            border_width=1,
            text_color=button_secondary_text,
            height=HEIGHT_MD,
            corner_radius=RADIUS_BUTTONS
        )
        cancel_button.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
        # Bind Enter key to save
        entry.bind("<Return>", lambda event: save_edit())
        entry.bind("<Escape>", lambda event: cancel_edit())

if __name__ == "__main__":
    app = App()
    app.mainloop()