import pandas as pd
import pymysql
from sqlalchemy import create_engine, text
import config

# --- Step 1: Read CSV created by Regions_to_Suburbs_Cleanup.py ---
df = pd.read_csv(config.INPUTFILENAME_REGIONS_SUBURB)

# --- Helper function for proper case ---
def to_proper_case(value):
    if pd.isna(value):
        return None
    return str(value).title()

# --- Step 2: Connect to MySQL ---
engine = create_engine(
    f"mysql+pymysql://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}/{config.DB_NAME}"
)

# --- Step 3: Transaction block ensures commit ---
with engine.begin() as conn:
    # Confirm database name
    db_name = conn.execute(text("SELECT DATABASE()")).scalar()
    print(f"\nConnected to database: {db_name}")

    # Check if table exists
    check_sql = text("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = :db AND table_name = :table
    """)
    exists = conn.execute(check_sql, {"db": db_name, "table": config.TABLE_NAME_Region_Suburb}).scalar()

    if exists == 0:
        print(f"Table {config.TABLE_NAME_Region_Suburb} does not exist. Creating...")

        # Create table with spatial index inline
        create_sql = f"""
        CREATE TABLE {config.TABLE_NAME_Region_Suburb} (
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            suburb VARCHAR(500),
            region VARCHAR(100),
            region_longitude DECIMAL(9,6),
            region_latitude DECIMAL(9,6),
            shape__are_left VARCHAR(100),
            shape__len_left VARCHAR(100),
            shape__are_right VARCHAR(100),
            shape__len_right VARCHAR(100),
            region_centroid VARCHAR(100),
            geometry GEOMETRY NOT NULL SRID 4326,
            SPATIAL INDEX idx_geometry (geometry)
        ) ENGINE=InnoDB;
        """
        conn.execute(text(create_sql))
        print("Table created successfully with spatial index.")
    else:
        # Table exists → check if it has data
        row_count = conn.execute(text(f"SELECT COUNT(*) FROM {config.TABLE_NAME_Region_Suburb}")).scalar()
        if row_count > 0:
            print(f"Table {config.TABLE_NAME_Region_Suburb} already contains {row_count} rows. Truncating...")
            conn.execute(text(f"TRUNCATE TABLE {config.TABLE_NAME_Region_Suburb}"))
            print("Table truncated. Ready for fresh import.")
        else:
            print(f"Table {config.TABLE_NAME_Region_Suburb} exists but is empty. Ready for import.")

    # --- Confirm indexes ---
    index_sql = text("""
        SELECT INDEX_NAME, COLUMN_NAME, INDEX_TYPE
        FROM information_schema.statistics
        WHERE table_schema = :db AND table_name = :table
    """)
    indexes = conn.execute(index_sql, {"db": db_name, "table": config.TABLE_NAME_Region_Suburb}).fetchall()

    print("\nIndexes on table:")
    for idx_name, col_name, idx_type in indexes:
        print(f" - {idx_name} on {col_name} ({idx_type})")

    # --- Print table fields ---
    columns_sql = text("""
        SELECT COLUMN_NAME, DATA_TYPE
        FROM information_schema.columns
        WHERE table_schema = :db AND table_name = :table
        ORDER BY ORDINAL_POSITION
    """)
    columns = conn.execute(columns_sql, {"db": db_name, "table": config.TABLE_NAME_Region_Suburb}).fetchall()

    print(f"\nTable confirmed: {config.TABLE_NAME_Region_Suburb}")
    print("Fields:")
    for col, dtype in columns:
        print(f" - {col} ({dtype})")

    # --- Insert rows with Proper Case ---
    insert_sql = text(f"""
        INSERT INTO {config.TABLE_NAME_Region_Suburb}
        (suburb, region, region_longitude, region_latitude,
         shape__are_left, shape__len_left, shape__are_right, shape__len_right,
         region_centroid, geometry)
        VALUES (:suburb, :region, :region_longitude, :region_latitude,
                :shape__are_left, :shape__len_left, :shape__are_right, :shape__len_right,
                :region_centroid, ST_GeomFromText(:geometry_wkt, 4326))
    """)

    total_rows = len(df)
    for i, row in df.iterrows():
        conn.execute(insert_sql, {
            "suburb": to_proper_case(row["Suburb"]),
            "region": to_proper_case(row["Region"]),
            "region_longitude": row["Region_Longitude"],
            "region_latitude": row["Region_Latitude"],
            "shape__are_left": row["Shape__Are_left"],
            "shape__len_left": row["Shape__Len_left"],
            "shape__are_right": row["Shape__Are_right"],
            "shape__len_right": row["Shape__Len_right"],
            "region_centroid": row["Region_Centroid"],
            "geometry_wkt": row["geometry_wkt"]
        })

        if (i + 1) % 50 == 0 or (i + 1) == total_rows:
            print(f"Inserted {i + 1} of {total_rows} rows...")

    print(f"\nImported {total_rows} rows into MySQL table {config.TABLE_NAME_Region_Suburb}")

    # --- Diagnostics ---
    diag_sql = text(f"""
        SELECT region, COUNT(*) AS suburb_count
        FROM {config.TABLE_NAME_Region_Suburb}
        GROUP BY region
        ORDER BY suburb_count DESC
    """)
    results = conn.execute(diag_sql).fetchall()

    print("\nDiagnostic Summary: Suburbs per Region")
    for region, count in results:
        print(f" - {region}: {count} suburbs")

    # --- Post-import row count ---
    final_count = conn.execute(text(f"SELECT COUNT(*) FROM {config.TABLE_NAME_Region_Suburb}")).scalar()
    print(f"\nFinal row count in {config.TABLE_NAME_Region_Suburb}: {final_count}")