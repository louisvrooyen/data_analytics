import pandas as pd
import mysql.connector
import os

# === CONFIGURATION ===
XLSX_PATH = r'E:\Downloads\Incident_Record_XLS.xlsx'
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
    'Incident_Category_ID',
    'Incident_Subcategory',
    'Incident_Subcategory_ID',
    'Str_Number',
    'Str_Name',
    'Suburb',
    'Town',
    'City',
    'Latitude',
    'Longitude'
]

# === CLEANING FUNCTION FOR DECIMAL FIELDS ===
def clean_decimal(value):
    if pd.isna(value):
        return None
    val = str(value).strip().upper()
    return None if val == 'NULL' or val == '' else value

# === CHECK FILE ACCESS ===
if not os.path.exists(XLSX_PATH):
    print(f"❌ File not found: {XLSX_PATH}")
    exit()

# === LOAD XLSX ===
try:
    df = pd.read_excel(XLSX_PATH, header=0)
    print(f"📄 Loaded {len(df)} records from Excel.")
except Exception as e:
    print(f"❌ Failed to read Excel file: {e}")
    exit()

# Drop 'ID' if present
if 'ID' in df.columns:
    df.drop(columns=['ID'], inplace=True)

# Drop any columns named 'nan' (from malformed headers)
df.drop(columns=[col for col in df.columns if str(col).lower() == 'nan'], inplace=True)

# === VALIDATE COLUMNS ===
csv_columns = df.columns.tolist()
missing = [col for col in expected_columns if col not in csv_columns]
extra = [col for col in csv_columns if col not in expected_columns]

if missing:
    print(f"❌ Missing columns in Excel: {missing}")
if extra:
    print(f"⚠️ Extra columns in Excel: {extra}")

if missing or extra:
    print("🛑 Column mismatch detected. Please fix the Excel headers before importing.")
    exit()
else:
    print("✅ Excel columns match MySQL schema.")

# === CLEAN Latitude and Longitude ===
df['Latitude'] = df['Latitude'].apply(clean_decimal)
df['Longitude'] = df['Longitude'].apply(clean_decimal)

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

# === PREPARE INSERT STATEMENTS ===
full_columns = expected_columns
partial_columns = [col for col in expected_columns if col not in ['Latitude', 'Longitude']]

full_insert_stmt = f"""
INSERT INTO `{TABLE_NAME}` ({', '.join([f"`{col}`" for col in full_columns])})
VALUES ({', '.join(['%s'] * len(full_columns))})
"""

partial_insert_stmt = f"""
INSERT INTO `{TABLE_NAME}` ({', '.join([f"`{col}`" for col in partial_columns])})
VALUES ({', '.join(['%s'] * len(partial_columns))})
"""

# === PREPARE ERROR INSERT STATEMENT ===
error_insert_stmt = f"""
INSERT INTO `{ERROR_TABLE}` ({', '.join([f"`{col}`" for col in safe_columns])}, `Error_Message`)
VALUES ({', '.join(['%s'] * len(safe_columns))}, %s)
"""

# === INSERT ROWS WITH FEEDBACK AND ERROR LOGGING ===
inserted_count = 0
error_count = 0

for index, row in df.iterrows():
    lat = row.get('Latitude')
    lon = row.get('Longitude')
    try:
        if lat is None or lon is None:
            values = [row.get(col) for col in partial_columns]
            cursor.execute(partial_insert_stmt, values)
        else:
            values = [row.get(col) for col in full_columns]
            cursor.execute(full_insert_stmt, values)
        print(f"Inserted row {index + 1} with ID: {cursor.lastrowid}")
        inserted_count += 1
    except Exception as e:
        print(f"⚠️ Failed to insert row {index + 1}: {e}")
        error_data = [
            None if pd.isna(row.get(col)) or str(row.get(col)).strip().upper() == 'NULL' or str(row.get(col)).strip() == ''
            else row.get(col)
            for col in safe_columns
        ] + [str(e)]
        try:
            cursor.execute(error_insert_stmt, error_data)
            error_count += 1
        except Exception as log_err:
            print(f"❌ Failed to log error row {index + 1}: {log_err}")

# === CLEANUP: Convert placeholder 0.00 to NULL ===
try:
    cursor.execute(f"""
        UPDATE `{TABLE_NAME}`
        SET Latitude = NULL, Longitude = NULL
        WHERE Latitude = 0.00 AND Longitude = 0.00
    """)
    print("🧽 Converted placeholder coordinates (0.00) to NULL.")
except Exception as cleanup_err:
    print(f"⚠️ Failed to update placeholders to NULL: {cleanup_err}")

conn.commit()
cursor.close()
conn.close()

# === FINAL STATUS ===
print(f"\n✅ Excel data inserted into `{TABLE_NAME}`.")
print(f"📦 Total records inserted: {inserted_count}")
print(f"🧾 Total errors logged to `{ERROR_TABLE}`: {error_count}")