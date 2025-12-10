import pandas as pd
from sqlalchemy import create_engine, text
import sys
import os
import config

# Check if file exists
if not os.path.exists(config.FILENAME):
    raise FileNotFoundError(f"CSV file not found: {config.FILENAME}")

# Load CSV with correct separator
df = pd.read_csv(config.FILENAME, sep=";")

# Round Lat/Lon to 6 decimals
if "Longitude" in df.columns and "Latitude" in df.columns:
    df["Longitude"] = df["Longitude"].round(6)
    df["Latitude"] = df["Latitude"].round(6)

# Convert column names to Proper Case
df.columns = [col.title().replace("_", " ") for col in df.columns]

# Create SQLAlchemy engine
engine = create_engine(
    f"mysql+pymysql://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}/{config.DB_NAME}"
)

# Optional: pre-create table schema
with engine.connect() as conn:
    conn.execute(text(f"""
        CREATE TABLE IF NOT EXISTS {config.TABLE_NAME} (
            ID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            Fire_Station VARCHAR(100),
            Code VARCHAR(10),
            Geometry TEXT,
            Longitude DECIMAL(9,6),
            Latitude DECIMAL(9,6)
        );
    """))

# Import CSV into MySQL
df.to_sql(config.TABLE_NAME, con=engine, if_exists="replace", index=False)

print(f"CSV imported successfully into MySQL table: {config.TABLE_NAME}")