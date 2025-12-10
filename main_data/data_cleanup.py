import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
from cleaning_logic import clean_text  # <-- import from separate file

# === CONFIGURATION ===
DB_USER = 'root'
DB_PASSWORD = 'Qwedcxzao0)16'
DB_HOST = 'localhost'
DB_NAME = 'incidents'
TABLE_NAME = 'incident_records'
TARGET_COLUMNS = ['Str_Name', 'Suburb']

# === SQLAlchemy ENGINE ===
engine = create_engine(f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}")

print(f"🔧 SQLAlchemy version: {sqlalchemy.__version__}")

# === LOAD DATA FROM MYSQL ===
df = pd.read_sql(f"SELECT * FROM `{TABLE_NAME}`", engine)
print(f"📄 Loaded {len(df)} records from `{TABLE_NAME}`.")

# === BEFORE PREVIEW ===
print("\n🔎 BEFORE CLEANUP (first 5 rows):")
print(df[TARGET_COLUMNS].head())

# === APPLY CLEANUP ===
for col in TARGET_COLUMNS:
    if col in df.columns:
        df[col] = df[col].apply(clean_text)

# === AFTER PREVIEW ===
print("\n✨ AFTER CLEANUP (first 5 rows):")
print(df[TARGET_COLUMNS].head())

# === TRUNCATE TABLE FIRST (raw DBAPI) ===
raw_conn = engine.raw_connection()
cur = raw_conn.cursor()
cur.execute(f"TRUNCATE TABLE `{TABLE_NAME}`")
raw_conn.commit()
cur.close()
raw_conn.close()
print(f"🧹 Table `{TABLE_NAME}` truncated.")

# === BULK INSERT CLEANED DATA ===
df.to_sql(TABLE_NAME, engine, if_exists='append', index=False)
print(f"\n✅ Bulk inserted {len(df)} cleaned records into `{TABLE_NAME}`.")