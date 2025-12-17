import mysql.connector
import config
import random
from datetime import datetime

def get_connection():
    return mysql.connector.connect(
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        database=config.DB_NAME,
        autocommit=True
    )

def randomize_case(value: str) -> str:
    """Return the string in random case style."""
    styles = [
        str.upper,
        str.lower,
        lambda s: ''.join(
            c.upper() if random.random() > 0.5 else c.lower()
            for c in s
        )
    ]
    return random.choice(styles)(value)

def apply_spelling_errors(value: str) -> str:
    """Introduce spelling mistakes by replacing characters."""
    if not value:
        return value
    mapping = {
        "e": "#",
        "o": "0",
        "a": "@",
        "i": "^",
        "1": "^"   # changed from "!" to "^" to avoid breaking
    }
    new_val = ""
    for c in value:
        if c.lower() in mapping and random.random() < 0.5:
            new_val += mapping[c.lower()]
        else:
            new_val += c
    return new_val

def log_progress(overall_updated, total_rows, step_name, idx, step_total):
    """Print progress with timestamp."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] Progress: {overall_updated}/{total_rows} rows updated "
          f"({step_name}: {idx}/{step_total})")

def messify_data():
    conn = get_connection()
    cursor = conn.cursor()

    # Count total rows
    cursor.execute(f"SELECT COUNT(*) FROM {config.TABLE_NAME}")
    total_rows = cursor.fetchone()[0]

    # Fetch all rows
    cursor.execute(f"SELECT id, Str_name, Suburb FROM {config.TABLE_NAME}")
    all_rows = cursor.fetchall()

    # Shuffle once and split into disjoint groups
    random.shuffle(all_rows)
    target_case_rows = int(total_rows * 0.2)
    target_abbrev_rows = int(total_rows * 0.3)
    target_spelling_rows = int(total_rows * 0.4)

    case_rows = all_rows[:target_case_rows]
    abbrev_rows = all_rows[target_case_rows:target_case_rows+target_abbrev_rows]
    spelling_rows = all_rows[target_case_rows+target_abbrev_rows:
                             target_case_rows+target_abbrev_rows+target_spelling_rows]

    overall_updated = 0

    # --- Step 1: Messy case ---
    for idx, (ir_id, str_name, suburb) in enumerate(case_rows, start=1):
        new_str_name = randomize_case(str_name or "")
        new_suburb = randomize_case(suburb or "")
        cursor.execute(f"""
            UPDATE {config.TABLE_NAME}
            SET Str_name = %s, Suburb = %s
            WHERE id = %s
        """, (new_str_name, new_suburb, ir_id))
        overall_updated += cursor.rowcount

        if idx % 100 == 0 or idx == len(case_rows):
            log_progress(overall_updated, total_rows, "Step 1", idx, len(case_rows))

    # --- Step 2: Abbreviation replacements ---
    replacements = {
        " rd": [" Road"],
        " st": [" str", " street"],
        " ave": [" avenue"],
        " la": [" lne", " lane"]
    }
    for idx, (ir_id, str_name, _) in enumerate(abbrev_rows, start=1):
        if not str_name:
            continue
        new_str_name = str_name.lower()
        for key, options in replacements.items():
            if key in new_str_name:
                replacement = random.choice(options)
                new_str_name = new_str_name.replace(key, replacement)
                break
        cursor.execute(f"""
            UPDATE {config.TABLE_NAME}
            SET Str_name = %s
            WHERE id = %s
        """, (new_str_name, ir_id))
        overall_updated += cursor.rowcount

        if idx % 100 == 0 or idx == len(abbrev_rows):
            log_progress(overall_updated, total_rows, "Step 2", idx, len(abbrev_rows))

    # --- Step 3: Spelling mistakes + reset coords ---
    for idx, (ir_id, str_name, suburb) in enumerate(spelling_rows, start=1):
        new_str_name = apply_spelling_errors(str_name or "")
        new_suburb = apply_spelling_errors(suburb or "")
        cursor.execute(f"""
            UPDATE {config.TABLE_NAME}
            SET Str_name = %s,
                Suburb = %s,
                Latitude = 0.00,
                Longitude = 0.00
            WHERE id = %s
        """, (new_str_name, new_suburb, ir_id))
        overall_updated += cursor.rowcount

        if idx % 100 == 0 or idx == len(spelling_rows):
            log_progress(overall_updated, total_rows, "Step 3", idx, len(spelling_rows))

    cursor.close()
    conn.close()

    print(f"🎯 All done. Table rows: {total_rows}, Total updated: {overall_updated}")

if __name__ == "__main__":
    messify_data()