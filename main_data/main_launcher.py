# main_launcher.py

import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

FORCED_PYTHON = r"E:\Python\python.exe"

def get_base_dir():
    if hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_dir()
SCRIPT_DIR = BASE_DIR

SCRIPTS = {
    "Import CSV": "import_csv.py",
    "Add Streets Data": "add_Streets_Data.py",
    "Generate Errors": "generate_errors.py"
}

MODULE_COMMAND = [
    FORCED_PYTHON,
    "-m",
    "data_imports_project.main_data.generate_data"
]

ICON_PATH = os.path.join(os.path.dirname(BASE_DIR), "Images", "dashboard.ico")


# --------------------------------------------------
# PROCESS LAUNCHING
# --------------------------------------------------

def launch_module():
    try:
        subprocess.Popen(
            MODULE_COMMAND,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    except Exception as e:
        messagebox.showerror("Error", "Failed to launch module:\n{}".format(e))


def launch_script(script_name):
    script_path = os.path.join(SCRIPT_DIR, script_name)

    if not os.path.exists(script_path):
        messagebox.showerror("Error", "Script not found:\n{}".format(script_path))
        return

    try:
        subprocess.Popen(
            [FORCED_PYTHON, script_path],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    except Exception as e:
        messagebox.showerror("Error", "Failed to launch script:\n{}".format(e))


# --------------------------------------------------
# DARK MODE GUI
# --------------------------------------------------

class DashboardGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dashboard Launcher")
        self.root.geometry("420x300")
        self.root.resizable(False, False)

        try:
            self.root.iconbitmap(ICON_PATH)
        except:
            pass

        self.bg = "#1e1e1e"
        self.fg = "#e0e0e0"
        self.btn_bg = "#333333"
        self.btn_fg = "#ffffff"
        self.btn_hover = "#444444"

        self.root.configure(bg=self.bg)

        self.build_gui()

    def hover_on(self, event):
        event.widget.config(bg=self.btn_hover)

    def hover_off(self, event):
        event.widget.config(bg=self.btn_bg)

    def build_gui(self):
        title = tk.Label(
            self.root,
            text="Dashboard Tools",
            font=("Segoe UI", 16, "bold"),
            bg=self.bg,
            fg=self.fg
        )
        title.pack(pady=15)

        frame = tk.Frame(self.root, bg=self.bg)
        frame.pack()

        self.create_button(
            frame,
            "Generate Data (Module)",
            launch_module
        )

        for label, script in SCRIPTS.items():
            self.create_button(
                frame,
                label,
                lambda s=script: launch_script(s)
            )

        close_btn = tk.Button(
            self.root,
            text="Close App",
            font=("Segoe UI", 10, "bold"),
            bg="#990000",
            fg="white",
            width=15,
            command=self.root.destroy
        )
        close_btn.pack(pady=15)

    def create_button(self, parent, text, command):
        btn = tk.Button(
            parent,
            text=text,
            font=("Segoe UI", 10),
            bg=self.btn_bg,
            fg=self.btn_fg,
            width=28,
            relief="flat",
            command=command
        )
        btn.pack(pady=5)

        btn.bind("<Enter>", self.hover_on)
        btn.bind("<Leave>", self.hover_off)


# --------------------------------------------------
# MAIN ENTRY
# --------------------------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardGUI(root)
    root.mainloop()