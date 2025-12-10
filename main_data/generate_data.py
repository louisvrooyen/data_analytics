# generate_data.py

import os
from datetime import datetime
from tkinter import ttk, messagebox

# Import dictionary of incident categories directly from categories.py
from data_imports_project.dictionaries.categories import incident_categories

# Import functions and constants from main_data modules
from data_imports_project.main_data.data_generator import (
    generate_records,
    write_csv,
    write_xlsx,
    HEADER,
)
from data_imports_project.main_data.gui_builder import create_gui


def launch_gui():
    gui = create_gui()
    root = gui["root"]
    start_picker = gui["start_picker"]
    end_picker = gui["end_picker"]
    record_entry = gui["record_entry"]
    format_choice = gui["format_choice"]
    preview_frame = gui["preview_frame"]
    tree = gui["tree"]
    preview_columns = gui["preview_columns"]

    # --- Status Bar ---
    status_var = ttk.Label(root, text="Ready", anchor="w", relief="sunken")
    status_var.grid(row=7, column=0, columnspan=2, sticky="we", padx=5, pady=5)

    def set_status(message: str):
        status_var.config(text=message)

    def update_preview(records):
        tree.delete(*tree.get_children())
        tree["columns"] = preview_columns
        for col in preview_columns:
            tree.heading(col, text=col)
            tree.column(col, width=140)
        for row in records:
            filtered = [row[i] for i in range(len(preview_columns))]
            tree.insert("", "end", values=filtered)
        preview_frame.grid()
        set_status(f"Previewed {len(records)} records")

    def on_preview():
        start = datetime.combine(start_picker.get_date(), datetime.min.time())
        end = datetime.combine(end_picker.get_date(), datetime.min.time())
        preview = generate_records(start, end, 20)
        update_preview(preview)

    def on_generate():
        try:
            start = datetime.combine(start_picker.get_date(), datetime.min.time())
            end = datetime.combine(end_picker.get_date(), datetime.min.time())
            count = int(record_entry.get())
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid number of records.")
            set_status("Error: Invalid record count")
            return

        filetype = format_choice.get().lower()
        records = generate_records(start, end, count)

        # Fixed output directory and filename
        output_dir = r"D:\Python\data_imports_project\csv_files"
        filename = os.path.join(output_dir, "load_data.csv")

        # Ensure directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Delete existing file if present
        if os.path.exists(filename):
            os.remove(filename)

        # Write file
        if filetype == "csv":
            write_csv(records, filename, HEADER)
        elif filetype == "xlsx":
            write_xlsx(records, filename, HEADER)
        else:
            messagebox.showerror("Error", f"Unsupported format: {filetype}")
            set_status("Error: Unsupported format")
            return

        messagebox.showinfo(
            "File Generated",
            f"✅ File '{filename}' created with {count} records."
        )
        update_preview(records[:20])
        set_status(f"File '{filename}' generated with {count} records")

    # Buttons
    preview_btn = ttk.Button(root, text="Preview 20 Records", command=on_preview)
    preview_btn.grid(row=4, column=0, pady=10)

    generate_btn = ttk.Button(root, text="Generate File", command=on_generate)
    generate_btn.grid(row=4, column=1, pady=10)

    close_btn = ttk.Button(root, text="Close", command=root.destroy)
    close_btn.grid(row=5, column=0, columnspan=2, pady=5)

    root.mainloop()


if __name__ == "__main__":
    launch_gui()