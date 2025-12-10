import mysql.connector
import config   # import your config file with DB_USER, DB_PASSWORD, etc.

# -------------------------------
# Core cleanup function
# -------------------------------
def clean_text(value: str) -> str:
    if not value:
        return value

    # Step 1: Proper Case
    value = value.title()

    # Step 2: Symbol replacements (literal, no regex)
    replacements = {
        "@": "a",
        "0": "o",
        "!": "i",
        "#": "e",
        "'S": "'s",
        "Streetr": "Street",
        "Avenuenue": "Avenue",
        "(R1O": "(R10",
        "(R31O": "(R310)",
        "1O": "10",
        "Lanene": "Lane",
        "1o":"10"
    }
    for k, v in replacements.items():
        value = value.replace(k, v)

    # Step 3: Suffixes word-by-word
    suffix_map = {
        "rd": "Road", "st": "Street", "str": "Street", "ave": "Avenue",
        "cl": "Close", "ter": "Terrace", "cr": "Crescent", "cir": "Circle",
        "sq": "Square", "blvd": "Boulevard", "la": "Lane", "dr": "Drive",
        "ext": "Extension", "pl": "Place", "wk": "Walk", "ct": "Court",
        "1st": "1st", "2nd": "2nd", "3rd": "3rd", "4th": "4th", "5th": "5th",
        "6th": "6th", "7th": "7th", "8th": "8th", "9th": "9th", "10th": "10th",
        "11th": "11th", "12th": "12th", "13th": "13th", "14th": "14th",
        "15th": "15th", "16th": "16th", "17th": "17th", "35th": "35th",
        "51st": "51st"
    }

    words = value.split()
    words = [suffix_map.get(w.lower(), w) for w in words]
    return " ".join(words)


# -------------------------------
# MySQL cleanup with debug prints
# -------------------------------
def clean_mysql():
    conn = mysql.connector.connect(
        host=config.DB_HOST,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME
    )
    cur = conn.cursor()

    cur.execute(f"SELECT {config.PRIMARY_KEY}, Str_Name, Suburb FROM {config.TABLE_NAME}")
    rows = cur.fetchall()

    updates = []
    for pk, str_name, suburb in rows:
        cleaned_str = clean_text(str_name)
        cleaned_suburb = clean_text(suburb)

        # Debug print to show what will be updated
        if cleaned_str != str_name or cleaned_suburb != suburb:
            print(f"Updating {config.PRIMARY_KEY}={pk}: "
                  f"Str_Name '{str_name}' -> '{cleaned_str}', "
                  f"Suburb '{suburb}' -> '{cleaned_suburb}'")
            updates.append((cleaned_str, cleaned_suburb, pk))

        else:
            print(f"No change for {config.PRIMARY_KEY}={pk}: "
                  f"Str_Name '{str_name}', Suburb '{suburb}'")

        # Batch commit
        if len(updates) >= config.BATCH_SIZE:
            cur.executemany(
                f"UPDATE {config.TABLE_NAME} SET Str_Name=%s, Suburb=%s WHERE {config.PRIMARY_KEY}=%s",
                updates
            )
            conn.commit()
            print(f"Committed batch of {len(updates)} updates.")
            updates = []

    # Final commit
    if updates:
        cur.executemany(
            f"UPDATE {config.TABLE_NAME} SET Str_Name=%s, Suburb=%s WHERE {config.PRIMARY_KEY}=%s",
            updates
        )
        conn.commit()
        print(f"Committed final batch of {len(updates)} updates.")

    conn.close()
    print("MySQL cleanup complete.")


# -------------------------------
# Example usage
# -------------------------------
if __name__ == "__main__":
    clean_mysql()