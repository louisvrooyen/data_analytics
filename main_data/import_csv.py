# import_csv.py

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import pandas as pd
import mysql.connector
import os
import datetime

# ---------------------------
# GUI APPLICATION
# ---------------------------

class CSVImporterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV → MySQL Import Tool")
        self.root.geometry("650x550")
        self.root.resizable(False, False)

        # ---------------------------
        # VARIABLES
        # ---------------------------
        self.csv_path = tk.StringVar()
        self.host = tk.StringVar(value="localhost")
        self.user = tk.StringVar(value="root")
        self.password = tk.StringVar(value="")
        self.database = tk.StringVar(value="incidents")
        self.table_name = tk.StringVar(value="incident_records")
        self.error_table = tk.StringVar(value="Errors")

        # Expected columns
        self.expected_columns = [
            'Incident_Number', 'Incident_Date', 'Incident_Category',
            'Incident_Subcategory', 'Str_Number', 'Incident_Save',
            'Incident_Ack', 'Veh_Desp', 'Veh_Arrived', 'Last_Veh_Home',
            'Incident_Closed', 'Incident_Status_ID', 'Service_Trip_ID',
            'Service_Trip_Reason'
        ]

        # ---------------------------
        # BUILD GUI
        # ---------------------------
        self.build_gui()

    def build_gui(self):
        # CSV File Picker
        tk.Label(self.root, text="CSV File:", font=("Segoe UI", 10)).place(x=20, y=20)
        tk.Entry(self.root, textvariable=self.csv_path, width=50).place(x=120, y=20)
        tk.Button(self.root, text="Browse", command=self.browse_csv).place(x=520, y=16)

        # Database Config
        tk.Label(self.root, text="Host:", font=("Segoe UI", 10)).place(x=20, y=60)
        tk.Entry(self.root, textvariable=self.host, width=20).place(x=120, y=60)

        tk.Label(self.root, text="User:", font=("Segoe UI", 10)).place(x=20, y=90)
        tk.Entry(self.root, textvariable=self.user, width=20).place(x=120, y=90)

        tk.Label(self.root, text="Password:", font=("Segoe UI", 10)).place(x=20, y=120)
        tk.Entry(self.root, textvariable=self.password, width=20, show="*").place(x=120, y=120)

        tk.Label(self.root, text="Database:", font=("Segoe UI", 10)).place(x=20, y=150)
        tk.Entry(self.root, textvariable=self.database, width=20).place(x=120, y=150)

        tk.Label(self.root, text="Table Name:", font=("Segoe UI", 10)).place(x=20, y=180)
        tk.Entry(self.root, textvariable=self.table_name, width=20).place(x=120, y=180)

        tk.Label(self.root, text="Error Table:", font=("Segoe UI", 10)).place(x=20, y=210)
        tk.Entry(self.root, textvariable=self.error_table, width=20).place(x=120, y=210)

        # Run Button
        tk.Button(self.root, text="Run Import", font=("Segoe UI", 11, "bold"),
                  bg="#4CAF50", fg="white", width=20, command=self.run_import).place(x=20, y=250)

        # Log Window
        tk.Label(self.root, text="Log Output:", font=("Segoe UI", 10)).place(x=20, y=300)
        self.log = scrolledtext.ScrolledText(self.root, width=78, height=12, font=("Consolas", 9))
        self.log.place(x=20, y=330)

    # ---------------------------
    # LOGGING
    # ---------------------------
    def log_write(self, text):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log.insert(tk.END, f"[{timestamp}] {text}\n")
        self.log.see(tk.END)

    # ---------------------------
    # FILE PICKER
    # ---------------------------
    def browse_csv(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if file_path:
            self.csv_path.set(file_path)

    # ---------------------------
    # MAIN IMPORT LOGIC
    # ---------------------------
    def run_import(self):
        csv_path = self.csv_path.get()

        if not os.path.exists(csv_path):
            messagebox.showerror("Error", "CSV file not found.")
            return

        self.log_write(f"Loading CSV: {csv_path}")

        # Load CSV
        try:
            df = pd.read_csv(csv_path)
            self.log_write(f"Loaded {len(df)} records.")
        except Exception as e:
            self.log_write(f"Failed to read CSV: {e}")
            return

        # Connect to MySQL
        try:
            conn = mysql.connector.connect(
                host=self.host.get(),
                user=self.user.get(),
                password=self.password.get(),
                database=self.database.get()
            )
            cursor = conn.cursor()
            self.log_write("Connected to MySQL.")
        except Exception as e:
            self.log_write(f"MySQL connection error: {e}")
            return

        table = self.table_name.get()
        error_table = self.error_table.get()

        # Check table count
        cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
        count = cursor.fetchone()[0]

        if count > 0:
            self.log_write(f"Table `{table}` has {count} rows. Truncating...")
            cursor.execute(f"TRUNCATE TABLE `{table}`")
            self.log_write("Table truncated.")

        # Ensure error table exists
        safe_cols = [col for col in self.expected_columns]
        error_cols_sql = ", ".join([f"`{c}` TEXT" for c in safe_cols])

        create_error_table = f"""
        CREATE TABLE IF NOT EXISTS `{error_table}` (
            `Error_ID` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            {error_cols_sql},
            `Error_Message` TEXT,
            `Logged_At` DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_error_table)

        # Insert data
        inserted = 0
        errors = 0

        placeholders = ", ".join(["%s"] * len(self.expected_columns))
        insert_sql = f"INSERT INTO `{table}` ({', '.join(self.expected_columns)}) VALUES ({placeholders})"

        for _, row in df.iterrows():
            try:
                values = [row[col] if col in row else None for col in self.expected_columns]
                cursor.execute(insert_sql, values)
                inserted += 1
            except Exception as e:
                error_values = [str(row[col]) if col in row else None for col in self.expected_columns]
                error_sql = f"""
                INSERT INTO `{error_table}` ({', '.join(self.expected_columns)}, Error_Message)
                VALUES ({', '.join(['%s']*len(self.expected_columns))}, %s)
                """
                cursor.execute(error_sql, error_values + [str(e)])
                errors += 1

        conn.commit()
        cursor.close()
        conn.close()

        self.log_write(f"Import complete.")
        self.log_write(f"Inserted: {inserted}")
        self.log_write(f"Errors logged: {errors}")
        messagebox.showinfo("Done", "CSV import completed successfully.")

# ---------------------------
# RUN APPLICATION
# ---------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = CSVImporterGUI(root)
    root.mainloop()