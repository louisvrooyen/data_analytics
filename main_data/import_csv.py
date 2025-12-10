import pandas as pd
import mysql.connector
import os

# === CONFIGURATION ===
CSV_PATH = r'D:\Python\data_imports_project\csv_files\load_data.csv'
TABLE_NAME = 'incident_records'
ERROR_TABLE = 'Errors'
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Qwedcxzao0)16',
    'database': 'incidents'
}

# === EXPECTED COLUMNS (excluding auto-increment ID) ===
expected_columns = [
    'Incident_Number',
    'Incident_Date',
    'Incident_Category',
    'Incident_Subcategory',
    'Str_Number',
    'Incident_Save',
    'Incident_Ack',
    'Veh_Desp',
    'Veh_Arrived',
    'Last_Veh_Home',
    'Incident_Closed',
    'Incident_Status_ID',
    'Service_Trip_ID',
    'Service_Trip_Reason'
]

# === CHECK FILE ACCESS ===
if not os.path.exists(CSV_PATH):
    print(f"❌ File not found: {CSV_PATH}")
    exit()

# === LOAD CSV ===
try:
    df = pd.read_csv(CSV_PATH, header=0)
    print(f"📄 Loaded {len(df)} records from CSV.")
except Exception as e:
    print(f"❌ Failed to read CSV: {e}")
    exit()

# === CONNECT TO MYSQL ===
try:
    conn = mysql.connector.connect(**DB_CONFIG)
    if conn.is_connected():
        print("✅ Connected to MySQL.")
    else:
        print("❌ Connection failed.")
        exit()
except mysql.connector.Error as err:
    print(f"❌ MySQL connection error: {err}")
    exit()

cursor = conn.cursor()

# === CHECK IF TABLE HAS DATA AND TRUNCATE ===
cursor.execute(f"SELECT COUNT(*) FROM `{TABLE_NAME}`")
row_count = cursor.fetchone()[0]

if row_count > 0:
    print(f"⚠️ Table `{TABLE_NAME}` contains {row_count} records. Truncating...")
    cursor.execute(f"TRUNCATE TABLE `{TABLE_NAME}`")
    print("🧹 Table truncated.")

# === ENSURE ERROR TABLE EXISTS ===
safe_columns = [col for col in expected_columns if str(col).lower() != 'nan']
error_columns_sql = ', '.join([f"`{col}` TEXT" for col in safe_columns])
create_error_table = f"""
CREATE TABLE IF NOT EXISTS `{ERROR_TABLE}` (
    `Error_ID` INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    {error_columns_sql},
    `Error_Message` TEXT,
    `Logged_At` DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""
cursor.execute(create_error_table)

# === INSERT DATA ===
inserted_count = 0
error_count = 0

placeholders = ', '.join(['%s'] * len(expected_columns))
insert_sql = f"INSERT INTO `{TABLE_NAME}` ({', '.join(expected_columns)}) VALUES ({placeholders})"

for _, row in df.iterrows():
    try:
        values = [row[col] if col in row else None for col in expected_columns]
        cursor.execute(insert_sql, values)
        inserted_count += 1
    except Exception as e:
        error_values = [str(row[col]) if col in row else None for col in expected_columns]
        error_sql = f"INSERT INTO `{ERROR_TABLE}` ({', '.join(expected_columns)}, Error_Message) VALUES ({', '.join(['%s']*len(expected_columns))}, %s)"
        cursor.execute(error_sql, error_values + [str(e)])
        error_count += 1

conn.commit()
cursor.close()
conn.close()

# === FINAL STATUS ===
print(f"\n✅ CSV data inserted into `{TABLE_NAME}`.")
print(f"📦 Total records inserted: {inserted_count}")
print(f"🧾 Total errors logged to `{ERROR_TABLE}`: {error_count}")