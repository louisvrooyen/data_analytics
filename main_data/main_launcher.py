import tkinter as tk
from tkinter import messagebox
import subprocess
import os

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

# Use pythonw.exe to avoid console windows
FORCED_PYTHON = r"E:\Python\pythonw.exe"

# Folder where your .py scripts live
SCRIPT_DIR = r"D:\Python\data_imports_project\main_data"

# Script mapping in your requested order
SCRIPTS = {
    "Generate Data": {
        "module": "data_imports_project.main_data.generate_data",
        "cwd": r"D:\Python",
        "py_path": r"D:\Python"
    },

    "Import CSV": "import_csv.py",
    "Update Data": "add_Streets_Data.py",
    "Messify Data": "generate_errors.py",
}

ICON_PATH = r"D:\Python\data_imports_project\Images\dashboard.ico"


# --------------------------------------------------
# PROCESS LAUNCHING
# --------------------------------------------------

def launch_script(script):
    try:
        # --- MODULE LAUNCH (Generate Data) ---
        if isinstance(script, dict):
            env = os.environ.copy()
            env["PYTHONPATH"] = script["py_path"]

            subprocess.Popen(
                [FORCED_PYTHON, "-m", script["module"]],
                cwd=script["cwd"],
                env=env
            )
            return

        # --- NORMAL SCRIPT LAUNCH (.py files) ---
        script_path = os.path.join(SCRIPT_DIR, script)

        if not os.path.exists(script_path):
            messagebox.showerror("Error", f"Script not found:\n{script_path}")
            return

        subprocess.Popen([FORCED_PYTHON, script_path])

    except Exception as e:
        messagebox.showerror("Error", f"Failed to launch:\n{e}")


# --------------------------------------------------
# GUI
# --------------------------------------------------

class DashboardGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dashboard Launcher")
        self.root.geometry("400x350")
        self.root.resizable(False, False)

        try:
            self.root.iconbitmap(ICON_PATH)
        except:
            pass

        # Dark theme
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
            text="Dashboard",
            font=("Segoe UI", 16, "bold"),
            bg=self.bg,
            fg=self.fg
        )
        title.pack(pady=20)

        frame = tk.Frame(self.root, bg=self.bg)
        frame.pack()

        # Create buttons in your requested order
        for label, script in SCRIPTS.items():
            self.create_button(frame, label, lambda s=script: launch_script(s))

        close_btn = tk.Button(
            self.root,
            text="Close",
            font=("Segoe UI", 10, "bold"),
            bg="#990000",
            fg="white",
            width=15,
            command=self.root.destroy
        )
        close_btn.pack(pady=20)

    def create_button(self, parent, text, command):
        btn = tk.Button(
            parent,
            text=text,
            font=("Segoe UI", 11),
            bg=self.btn_bg,
            fg=self.btn_fg,
            width=25,
            relief="flat",
            command=command
        )
        btn.pack(pady=8)

        btn.bind("<Enter>", self.hover_on)
        btn.bind("<Leave>", self.hover_off)


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardGUI(root)
    root.mainloop()