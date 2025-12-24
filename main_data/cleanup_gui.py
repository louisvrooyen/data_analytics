# cleanup_gui.py

import tkinter as tk
from tkinter import scrolledtext, ttk
import subprocess
import threading
import os
import sys
import shlex

BASE = os.path.dirname(os.path.abspath(__file__))

def abs_path(filename):
    return os.path.join(BASE, filename)


# -------------------------
# Generic subprocess runner that streams stdout/stderr into a text widget
# -------------------------

def run_subprocess_with_output(cmd, text_widget):
    def worker():
        try:
            # Clear the widget
            text_widget.config(state=tk.NORMAL)
            text_widget.delete("1.0", tk.END)

            # Start process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            # Read stdout
            for line in process.stdout:
                text_widget.insert(tk.END, line)
                text_widget.see(tk.END)

            # Read stderr
            err_output = process.stderr.read()
            if err_output:
                text_widget.insert(tk.END, "\n[ERROR OUTPUT]\n", "error")
                text_widget.insert(tk.END, err_output)
                text_widget.see(tk.END)

            process.wait()

            text_widget.insert(tk.END, f"\n[Process exited with code {process.returncode}]\n")
            text_widget.see(tk.END)
            text_widget.config(state=tk.DISABLED)

        except Exception as e:
            text_widget.insert(tk.END, f"\n[EXCEPTION] {e}\n", "error")
            text_widget.see(tk.END)
            text_widget.config(state=tk.DISABLED)

    threading.Thread(target=worker, daemon=True).start()


# -------------------------
# GUI setup
# -------------------------

root = tk.Tk()
root.title("Python Data Cleanup")
root.geometry("900x600")

notebook = ttk.Notebook(root)
notebook.pack(fill=tk.BOTH, expand=True)

# ----- Tab 1: Batch Cleanup -----
tab_batch = ttk.Frame(notebook)
notebook.add(tab_batch, text="Batch Cleanup")

batch_text = scrolledtext.ScrolledText(tab_batch, wrap=tk.WORD, width=110, height=30)
batch_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

batch_text.tag_config("error", foreground="red")

btn_run_batch = tk.Button(
    tab_batch,
    text="Run Full Cleanup",
    height=2,
    width=20,
    command=lambda: run_subprocess_with_output(
        [sys.executable, abs_path("data_cleanup.py")],
        batch_text
    )
)
btn_run_batch.pack(pady=(0, 10))


# ----- Tab 2: Test Single Value -----
tab_test = ttk.Frame(notebook)
notebook.add(tab_test, text="Test Single Value")

# Input controls
input_frame = ttk.Frame(tab_test)
input_frame.pack(fill=tk.X, padx=10, pady=5)

lbl_type = ttk.Label(input_frame, text="Type:")
lbl_type.pack(side=tk.LEFT)

test_type_var = tk.StringVar(value="str")
opt_type = ttk.Combobox(
    input_frame,
    textvariable=test_type_var,
    values=["str", "suburb"],
    width=10,
    state="readonly"
)
opt_type.pack(side=tk.LEFT, padx=5)

lbl_value = ttk.Label(input_frame, text="Value:")
lbl_value.pack(side=tk.LEFT, padx=(10, 0))

entry_value = ttk.Entry(input_frame, width=60)
entry_value.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

def run_test():
    value = entry_value.get().strip()
    mode = test_type_var.get().strip().lower()
    if not value:
        return
    # Build command: python test_cleanup.py mode "value..."
    cmd = [sys.executable, abs_path("test_cleanup.py"), mode, value]
    run_subprocess_with_output(cmd, test_text)

btn_run_test = tk.Button(
    tab_test,
    text="Test Cleanup",
    height=2,
    width=20,
    command=run_test
)
btn_run_test.pack(pady=(0, 5))

test_text = scrolledtext.ScrolledText(tab_test, wrap=tk.WORD, width=110, height=25)
test_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
test_text.tag_config("error", foreground="red")

root.mainloop()