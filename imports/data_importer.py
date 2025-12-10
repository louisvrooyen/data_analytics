# data_importer.py

import pandas as pd
from sqlalchemy import create_engine
import config

def validate_columns(df, expected_columns, table_name):
    # Normalize both actual and expected columns to uppercase
    actual = [col.strip().upper() for col in df.columns]
    expected = [col.strip().upper() for col in expected_columns]

    missing = [col for col in expected if col not in actual]
    extra = [col for col in actual if col not in expected]

    if missing or extra:
        raise ValueError(
            f"❌ Column mismatch for table '{table_name}':\n"
            f"Missing columns: {missing}\n"
            f"Unexpected columns: {extra}"
        )

def import_excel_to_mysql(file_path, sheet_name, table_name, expected_columns):
    print(f"📥 Reading '{sheet_name}' from {file_path}...")
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    print(f"🔍 Validating columns for table '{table_name}'...")
    validate_columns(df, expected_columns, table_name)

    # Optional: normalize column names to uppercase to match MySQL schema
    df.columns = [col.strip().upper() for col in df.columns]

    engine = create_engine(
        f"mysql+mysqlconnector://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}/{config.DB_NAME}"
    )

    print(f"🚀 Importing {len(df)} rows into '{table_name}'...")
    df.to_sql(name=table_name, con=engine, if_exists="append", index=False)
    print(f"✅ Import complete for '{table_name}'\n")