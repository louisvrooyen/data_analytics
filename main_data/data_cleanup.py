# data_cleanup.py

import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, text as sql_text
import sys

from cleaning_logic import (
    clean_str_name,
    clean_suburb,
    ANSI_CYAN,
    ANSI_RED,
    ANSI_RESET
)


DB_USER = "root"
DB_PASSWORD = "Qwedcxzao0)16"
DB_HOST = "localhost"
DB_NAME = "incidents"
TABLE_NAME = "incident_records"

engine = create_engine(
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}",
    pool_pre_ping=True
)

def main():
    print(f"{ANSI_CYAN}Using SQLAlchemy {sqlalchemy.__version__}{ANSI_RESET:=^60}")

    try:
        df = pd.read_sql(f"SELECT * FROM `{TABLE_NAME}`", engine)
        print(f"{ANSI_CYAN}Loaded {len(df)} rows from `{TABLE_NAME}`{ANSI_RESET}")
    except Exception as e:
        print(f"{ANSI_RED}Failed to load data: {e}{ANSI_RESET}")
        sys.exit(1)

    col_map = {c.lower(): c for c in df.columns}
    str_col = col_map.get("str_name")
    suburb_col = col_map.get("suburb")

    if not str_col:
        print(f"{ANSI_RED}WARNING: No 'Str_Name' column found (case-insensitive).{ANSI_RESET}")
    if not suburb_col:
        print(f"{ANSI_RED}WARNING: No 'Suburb' column found (case-insensitive).{ANSI_RESET}")

    print(f"{ANSI_CYAN}Preview BEFORE cleanup:{ANSI_RESET}")
    preview_cols = [c for c in [str_col, suburb_col] if c]
    if preview_cols:
        print(df[preview_cols].head().to_string())
        print()

    # Full debug for ALL rows
    total = len(df)
    for idx in range(total):
        print(f"{ANSI_CYAN}================ ROW {idx+1}/{total} ================ {ANSI_RESET}")
        if str_col:
            original = df.at[idx, str_col]
            print(f"{ANSI_CYAN}--- CLEANING STR_NAME ---{ANSI_RESET}")
            print(f"ORIGINAL: {original}")
            cleaned = clean_str_name(original)
            df.at[idx, str_col] = cleaned
        if suburb_col:
            original_s = df.at[idx, suburb_col]
            print(f"{ANSI_CYAN}--- CLEANING SUBURB ---{ANSI_RESET}")
            print(f"ORIGINAL: {original_s}")
            cleaned_s = clean_suburb(original_s)
            df.at[idx, suburb_col] = cleaned_s

    print(f"{ANSI_CYAN}Preview AFTER cleanup:{ANSI_RESET}")
    if preview_cols:
        print(df[preview_cols].head().to_string())
        print()

    # Write back
    try:
        with engine.begin() as conn:
            conn.execute(sql_text(f"TRUNCATE TABLE `{TABLE_NAME}`"))
            df.to_sql(TABLE_NAME, conn, if_exists="append", index=False)
        print(f"{ANSI_CYAN}Wrote {len(df)} cleaned rows back to `{TABLE_NAME}`{ANSI_RESET}")
    except Exception as e:
        print(f"{ANSI_RED}Failed to write cleaned data: {e}{ANSI_RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()