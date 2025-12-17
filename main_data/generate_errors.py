import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from datetime import datetime
import mysql.connector
import config
import random

# --- Helpers ---
def get_connection():
    return mysql.connector.connect(
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        database=config.DB_NAME,
        autocommit=True
    )

def randomize_case(value: str) -> str:
    styles = [
        str.upper,
        str.lower,
        lambda s: ''.join(c.upper() if random.random() > 0.5 else c.lower() for c in s)
    ]
    return random.choice(styles)(value)

def apply_spelling_errors(value: str) -> str:
    if not value:
        return value
    mapping = {"e": "#", "o": "0", "a": "@", "i": "^", "1": "^"}
    new_val = ""
    for c in value:
        if c.lower() in mapping and random.random() < 0.5:
            new_val += mapping[c.lower()]
        else:
            new_val += c
    return new_val

def log_progress(text_widget, progress_bar, overall_updated, total_rows, step_name, idx, step_total):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"[{ts}] Progress: {overall_updated}/{total_rows} rows updated ({step_name}: {idx}/{step_total})\n"
    text_widget.insert(tk.END, msg)
    text_widget.see(tk.END)
    progress_bar["value"] = overall_updated
    progress_bar.update()

# --- Main messify function ---
def messify_data(text_widget, progress_bar):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(f"SELECT COUNT(*) FROM {config.TABLE_NAME}")
    total_rows = cursor.fetchone()[0]

    cursor.execute(f"SELECT id, Str_name, Suburb FROM {config.TABLE_NAME}")
    all_rows = cursor.fetchall()
    random.shuffle(all_rows)

    target_case_rows = int(total_rows * 0.2)
    target_abbrev_rows = int(total_rows * 0.3)
    target_spelling_rows = int(total_rows * 0.4)

    case_rows = all_rows[:target_case_rows]
    abbrev_rows = all_rows[target_case_rows:target_case_rows+target_abbrev_rows]
    spelling_rows = all_rows[target_case_rows+target_abbrev_rows:
                             target_case_rows+target_abbrev_rows+target_spelling_rows]

    overall_updated = 0
    progress_bar["maximum"] = total_rows

    # Step 1
    for idx, (ir_id, str_name, suburb) in enumerate(case_rows, start=1):
        new_str_name = randomize_case(str_name or "")
        new_suburb = randomize_case(suburb or "")
        cursor.execute(f"UPDATE {config.TABLE_NAME} SET Str_name=%s, Suburb=%s WHERE id=%s",
                       (new_str_name, new_suburb, ir_id))
        overall_updated += cursor.rowcount
        if idx % 100 == 0 or idx == len(case_rows):
            log_progress(text_widget, progress_bar, overall_updated, total_rows, "Step 1", idx, len(case_rows))

    # Step 2
    replacements = {" rd": [" Road"], " st": [" str", " street"], " ave": [" avenue"], " la": [" lne", " lane"]}
    for idx, (ir_id, str_name, _) in enumerate(abbrev_rows, start=1):
        if not str_name:
            continue
        new_str_name = str_name.lower()
        for key, options in replacements.items():
            if key in new_str_name:
                new_str_name = new_str_name.replace(key, random.choice(options))
                break
        cursor.execute(f"UPDATE {config.TABLE_NAME} SET Str_name=%s WHERE id=%s", (new_str_name, ir_id))
        overall_updated += cursor.rowcount
        if idx % 100 == 0 or idx == len(abbrev_rows):
            log_progress(text_widget, progress_bar, overall_updated, total_rows, "Step 2", idx, len(abbrev_rows))

    # Step 3
    for idx, (ir_id, str_name, suburb) in enumerate(spelling_rows, start=1):
        new_str_name = apply_spelling_errors(str_name or "")
        new_suburb = apply_spelling_errors(suburb or "")
        cursor.execute(f"""UPDATE {config.TABLE_NAME}
                           SET Str_name=%s, Suburb=%s, Latitude=0.00, Longitude=0.00
                           WHERE id=%s""", (new_str_name, new_suburb, ir_id))
        overall_updated += cursor.rowcount
        if idx % 100 == 0 or idx == len(spelling_rows):
            log_progress(text_widget, progress_bar, overall_updated, total_rows, "Step 3", idx, len(spelling_rows))

    cursor.close()
    conn.close()
    text_widget.insert(tk.END, f"\n🎯 All done. Table rows: {total_rows}, Total updated: {overall_updated}\n")
    text_widget.see(tk.END)

# --- GUI setup ---
def run_gui():
    root = tk.Tk()
    root.title("Messify Data Tool")

    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky="nsew")

    text_area = scrolledtext.ScrolledText(frame, width=100, height=25)
    text_area.grid(row=0, column=0, columnspan=2, pady=10)

    progress_bar = ttk.Progressbar(frame, orient="horizontal", length=600, mode="determinate")
    progress_bar.grid(row=1, column=0, columnspan=2, pady=5)

    def start_messify():
        text_area.insert(tk.END, "Starting messify process...\n")
        threading.Thread(target=messify_data, args=(text_area, progress_bar), daemon=True).start()

    start_button = ttk.Button(frame, text="Run Messify", command=start_messify)
    start_button.grid(row=2, column=0, pady=5)

    quit_button = ttk.Button(frame, text="Quit", command=root.destroy)
    quit_button.grid(row=2, column=1, pady=5)

    root.mainloop()

if __name__ == "__main__":
    run_gui()