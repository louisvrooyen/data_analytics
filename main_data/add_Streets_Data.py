import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from datetime import datetime
import mysql.connector
import config
import random

def get_connection():
    return mysql.connector.connect(
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        database=config.DB_NAME,
        autocommit=True
    )

def log_progress(text_widget, progress_bar, overall_updated, total_rows, batch_number, batch_idx, batch_total):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = (f"[{ts}] Batch {batch_number}, {batch_idx}/{batch_total} rows in batch, "
           f"{overall_updated}/{total_rows} overall ({(overall_updated/total_rows)*100:.2f}% complete)\n")
    text_widget.insert(tk.END, msg)
    text_widget.see(tk.END)
    progress_bar["value"] = overall_updated
    progress_bar.update()

def update_random_streets(text_widget, progress_bar, batch_size=200, progress_interval=100):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Get all street records
    cursor.execute("SELECT * FROM streets_lookup")
    street_rows = cursor.fetchall()
    street_count = len(street_rows)

    # Get all incident record IDs
    cursor.execute(f"SELECT id FROM {config.TABLE_NAME}")
    incident_ids = [row["id"] for row in cursor.fetchall()]
    incident_count = len(incident_ids)

    text_widget.insert(tk.END, f"Found {incident_count} incidents and {street_count} streets.\n")
    text_widget.see(tk.END)

    random.shuffle(street_rows)

    total_updated = 0
    batch_number = 1
    progress_bar["maximum"] = incident_count

    # Process incidents in batches
    for i in range(0, incident_count, batch_size):
        batch_ids = incident_ids[i:i+batch_size]

        for j, ir_id in enumerate(batch_ids, start=1):
            street = street_rows[(i + j) % street_count]

            update_sql = f"""
            UPDATE {config.TABLE_NAME}
            SET Str_name = %s,
                Suburb = %s,
                Town = %s,
                City = %s,
                Latitude = %s,
                Longitude = %s,
                X_Road = %s,
                Primary_Station = %s,
                Region_ID = %s,
                Region = %s
            WHERE id = %s
            """
            cursor.execute(update_sql, (
                street["Main_Road"],
                street["Suburb"],
                street["Town"],
                street["City"],
                street["XRoad_Latitude"],
                street["XRoad_Longitude"],
                street["X_Road"],
                street["Fire_Station"],
                street["Region_ID"],
                street["Region_Name"],
                ir_id
            ))
            total_updated += cursor.rowcount

            if j % progress_interval == 0 or j == len(batch_ids):
                log_progress(text_widget, progress_bar, total_updated, incident_count,
                             batch_number, j, len(batch_ids))

        text_widget.insert(tk.END, f"✅ Batch {batch_number} completed: {len(batch_ids)} rows updated\n")
        text_widget.see(tk.END)
        batch_number += 1

    cursor.close()
    conn.close()
    text_widget.insert(tk.END, f"\n🎯 All batches done. Total rows updated: {total_updated} (expected {incident_count})\n")
    text_widget.see(tk.END)

# --- GUI setup ---
def run_gui():
    root = tk.Tk()
    root.title("Update Random Streets Tool")

    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky="nsew")

    text_area = scrolledtext.ScrolledText(frame, width=100, height=25)
    text_area.grid(row=0, column=0, columnspan=2, pady=10)

    progress_bar = ttk.Progressbar(frame, orient="horizontal", length=600, mode="determinate")
    progress_bar.grid(row=1, column=0, columnspan=2, pady=5)

    def start_update():
        text_area.insert(tk.END, "Starting update process...\n")
        threading.Thread(target=update_random_streets,
                         args=(text_area, progress_bar, 300, 100),
                         daemon=True).start()

    start_button = ttk.Button(frame, text="Run Update", command=start_update)
    start_button.grid(row=2, column=0, pady=5)

    quit_button = ttk.Button(frame, text="Quit", command=root.destroy)
    quit_button.grid(row=2, column=1, pady=5)

    root.mainloop()

if __name__ == "__main__":
    run_gui()