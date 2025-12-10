import pymysql
from sqlalchemy import create_engine, text
import config

# --- Connect to MySQL ---
engine = create_engine(
    f"mysql+pymysql://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}/{config.DB_NAME}"
)

# --- List of columns you want to drop ---
columns_to_drop = ["Region_Number", "Old_Code", "Legacy_Field"]

with engine.begin() as conn:
    for col in columns_to_drop:
        # Step 1: Check if column exists
        check_column_sql = text("""
            SELECT COUNT(*)
            FROM information_schema.columns
            WHERE table_schema = :db
              AND table_name = :table
              AND column_name = :col
        """)
        exists = conn.execute(check_column_sql, {
            "db": config.DB_NAME,
            "table": "regions",
            "col": col
        }).scalar()

        # Step 2: Drop column only if it exists
        if exists > 0:
            print(f"Column {col} exists. Dropping...")
            conn.execute(text(f"ALTER TABLE regions DROP COLUMN {col}"))
            print(f"Column {col} dropped successfully.")
        else:
            print(f"Column {col} does not exist. Skipping...")