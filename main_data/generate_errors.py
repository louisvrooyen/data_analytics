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

def randomize_case(value: str) -> str:
    """Return the string in random case style."""
    styles = [
        str.upper,               # all upper
        str.lower,               # all lower
        lambda s: ''.join(
            c.upper() if random.random() > 0.5 else c.lower()
            for c in s           # mixed case
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
        "i": "!"
    }
    new_val = ""
    for c in value:
        if c.lower() in mapping and random.random() < 0.5:  # 50% chance per char
            new_val += mapping[c.lower()]
        else:
            new_val += c
    return new_val

def messify_data():
    conn = get_connection()
    cursor = conn.cursor()

    # Count total rows
    cursor.execute(f"SELECT COUNT(*) FROM {config.TABLE_NAME}")
    total_rows = cursor.fetchone()[0]

    # Fetch all rows
    cursor.execute(f"SELECT id, Str_name, Suburb FROM {config.TABLE_NAME}")
    all_rows = cursor.fetchall()

    # --- Step 1: Messy case on 20% ---
    target_case_rows = int(total_rows * 0.2)
    chosen_case_rows = random.sample(all_rows, target_case_rows)
    case_updated = 0
    for ir_id, str_name, suburb in chosen_case_rows:
        new_str_name = randomize_case(str_name or "")
        new_suburb = randomize_case(suburb or "")
        cursor.execute(f"""
            UPDATE {config.TABLE_NAME}
            SET Str_name = %s, Suburb = %s
            WHERE id = %s
        """, (new_str_name, new_suburb, ir_id))
        case_updated += cursor.rowcount
    print(f"✅ Step 1: Messy case applied to {case_updated} rows")

    # --- Step 2: Abbreviation replacements on 30% ---
    target_abbrev_rows = int(total_rows * 0.3)
    chosen_abbrev_rows = random.sample(all_rows, target_abbrev_rows)
    abbrev_updated = 0
    replacements = {
        " rd": [" Road"],
        " st": [" str", " street"],
        " ave": [" avenue"],
        " la": [" lne", " lane"]
    }
    for ir_id, str_name, _ in chosen_abbrev_rows:
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
        abbrev_updated += cursor.rowcount
    print(f"✅ Step 2: Abbreviation messiness applied to {abbrev_updated} rows")

    # --- Step 3: Spelling mistakes on 40% + reset coords ---
    target_spelling_rows = int(total_rows * 0.4)
    chosen_spelling_rows = random.sample(all_rows, target_spelling_rows)
    spelling_updated = 0
    for ir_id, str_name, suburb in chosen_spelling_rows:
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
        spelling_updated += cursor.rowcount
    print(f"✅ Step 3: Spelling mistakes + coord reset applied to {spelling_updated} rows")

    cursor.close()
    conn.close()
    print(f"🎯 All done. Total rows: {total_rows}, Step 1: {case_updated}, Step 2: {abbrev_updated}, Step 3: {spelling_updated}")

if __name__ == "__main__":
    messify_data()