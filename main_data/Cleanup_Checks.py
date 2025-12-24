# cleanup_checks.py

import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont
import mysql.connector
import config


# -------------------------
# Set global default font (Segoe UI)
# -------------------------

def set_default_font():
    default_font = tkfont.nametofont("TkDefaultFont")
    default_font.configure(family="Segoe UI", size=10)

    text_font = tkfont.nametofont("TkTextFont")
    text_font.configure(family="Segoe UI", size=10)

    fixed_font = tkfont.nametofont("TkFixedFont")
    fixed_font.configure(family="Segoe UI", size=10)

    menu_font = tkfont.nametofont("TkMenuFont")
    menu_font.configure(family="Segoe UI", size=10)

    heading_font = tkfont.nametofont("TkHeadingFont")
    heading_font.configure(family="Segoe UI", size=10, weight="bold")


# -------------------------
# Database connection helper
# -------------------------

def get_connection():
    return mysql.connector.connect(
        host=config.DB_HOST,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME
    )


# -------------------------
# Generic table viewer with pagination
# -------------------------

class TableWindow:
    def __init__(self, parent, title, columns, rows):
        self.rows = rows
        self.columns = columns
        self.page = 0
        self.page_size = 100

        self.win = tk.Toplevel(parent)
        self.win.title(title)
        self.win.geometry("900x600")

        # Frame for table
        frame = ttk.Frame(self.win)
        frame.pack(fill=tk.BOTH, expand=True)

        # Treeview
        self.tree = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200, anchor=tk.W)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Pagination controls
        nav = ttk.Frame(self.win)
        nav.pack(fill=tk.X)

        self.btn_prev = ttk.Button(nav, text="<< Prev", command=self.prev_page)
        self.btn_prev.pack(side=tk.LEFT, padx=5, pady=5)

        self.btn_next = ttk.Button(nav, text="Next >>", command=self.next_page)
        self.btn_next.pack(side=tk.LEFT, padx=5, pady=5)

        self.lbl_page = ttk.Label(nav, text="")
        self.lbl_page.pack(side=tk.LEFT, padx=10)

        self.refresh()

    def refresh(self):
        # Clear table
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Pagination slice
        start = self.page * self.page_size
        end = start + self.page_size
        page_rows = self.rows[start:end]

        for r in page_rows:
            self.tree.insert("", tk.END, values=r)

        total_pages = max(1, (len(self.rows) - 1) // self.page_size + 1)
        self.lbl_page.config(text=f"Page {self.page + 1} of {total_pages}")

        # Enable/disable buttons
        self.btn_prev.config(state=tk.NORMAL if self.page > 0 else tk.DISABLED)
        self.btn_next.config(state=tk.NORMAL if end < len(self.rows) else tk.DISABLED)

    def next_page(self):
        self.page += 1
        self.refresh()

    def prev_page(self):
        self.page -= 1
        self.refresh()


# -------------------------
# Query functions
# -------------------------

def run_str_name_check(filter_letter=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT Str_Name, COUNT(*) AS Total
            FROM incidents.incident_records
        """

        if filter_letter:
            query += " WHERE Str_Name LIKE %s"
            cursor.execute(query + " GROUP BY Str_Name ORDER BY Str_Name", (filter_letter + "%",))
        else:
            cursor.execute(query + " GROUP BY Str_Name ORDER BY Str_Name")

        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        TableWindow(root, "Str_Name Cleanup Check", ["Str_Name", "Total"], rows)

    except Exception as e:
        messagebox.showerror("Error", str(e))


def run_suburb_check(filter_letter=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            SELECT COUNT(*) AS Total, Suburb
            FROM incidents.incident_records
            WHERE id BETWEEN 0 AND 100000
        """

        if filter_letter:
            query += " AND Suburb LIKE %s"
            cursor.execute(query + " GROUP BY Suburb ORDER BY Suburb", (filter_letter + "%",))
        else:
            cursor.execute(query + " GROUP BY Suburb ORDER BY Suburb")

        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        TableWindow(root, "Suburb Cleanup Check", ["Total", "Suburb"], rows)

    except Exception as e:
        messagebox.showerror("Error", str(e))


# -------------------------
# GUI Setup
# -------------------------

set_default_font()  # Apply Segoe UI globally

root = tk.Tk()
root.title("Cleanup Checks")
root.geometry("400x250")

title_lbl = ttk.Label(root, text="Cleanup Verification Tool", font=("Segoe UI", 14, "bold"))
title_lbl.pack(pady=10)

# Filter frame
filter_frame = ttk.Frame(root)
filter_frame.pack(pady=10)

ttk.Label(filter_frame, text="Filter by first letter (optional):").pack(side=tk.LEFT, padx=5)
filter_var = tk.StringVar()
filter_entry = ttk.Entry(filter_frame, textvariable=filter_var, width=5)
filter_entry.pack(side=tk.LEFT)

# Buttons
btn1 = ttk.Button(root, text="Check Str_Name Cleanup",
                  command=lambda: run_str_name_check(filter_var.get().strip() or None))
btn1.pack(pady=5)

btn2 = ttk.Button(root, text="Check Suburb Cleanup",
                  command=lambda: run_suburb_check(filter_var.get().strip() or None))
btn2.pack(pady=5)

btn3 = ttk.Button(root, text="Close", command=root.destroy)
btn3.pack(pady=10)

root.mainloop()