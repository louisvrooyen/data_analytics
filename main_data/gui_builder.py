import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry

def create_gui():
    root = tk.Tk()
    root.title("Incident Record Generator")
    root.geometry("800x600")
    root.resizable(True, True)

    # --- Start Date ---
    ttk.Label(root, text="Start Date:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    start_picker = DateEntry(root, width=12, date_pattern="yyyy-mm-dd")
    start_picker.grid(row=0, column=1, padx=10, pady=5)

    # --- End Date ---
    ttk.Label(root, text="End Date:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    end_picker = DateEntry(root, width=12, date_pattern="yyyy-mm-dd")
    end_picker.grid(row=1, column=1, padx=10, pady=5)

    # --- Number of Records ---
    ttk.Label(root, text="Number of Records:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
    record_entry = ttk.Entry(root)
    record_entry.insert(0, "10000")
    record_entry.grid(row=2, column=1, padx=10, pady=5)

    # --- Output Format ---
    ttk.Label(root, text="Output Format:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
    format_choice = ttk.Combobox(root, values=["csv", "xlsx"], state="readonly")
    format_choice.set("csv")
    format_choice.grid(row=3, column=1, padx=10, pady=5)

    # --- Preview Frame ---
    preview_frame = ttk.Frame(root)
    preview_columns = [
        "Incident_Number", "Incident_Date", "Incident_Category",
        "Incident_Subcategory", "Str_Number", "Incident_Save", "Incident_Ack"
    ]

    tree = ttk.Treeview(preview_frame, show="headings", height=10, columns=preview_columns)
    scrollbar = ttk.Scrollbar(preview_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    for col in preview_columns:
        tree.heading(col, text=col)
        tree.column(col, width=140)

    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    preview_frame.grid(row=6, column=0, columnspan=2, padx=10, pady=10)
    preview_frame.grid_remove()

    return {
        "root": root,
        "start_picker": start_picker,
        "end_picker": end_picker,
        "record_entry": record_entry,
        "format_choice": format_choice,
        "preview_frame": preview_frame,
        "tree": tree,
        "preview_columns": preview_columns
    }

# --- Optional test harness ---
if __name__ == "__main__":
    gui = create_gui()
    gui["root"].mainloop()