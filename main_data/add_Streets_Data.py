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

def update_random_streets(batch_size=200):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Get all street records
    cursor.execute("SELECT * FROM streets_lookup")
    street_rows = cursor.fetchall()
    street_count = len(street_rows)

    # Get all incident record IDs
    cursor.execute(f"SELECT id FROM {config.TABLE_NAME}")
    incident_ids = [row["id"] for row in cursor.fetchall()]
    incident_count = len(incident_ids)

    print(f"Found {incident_count} incidents and {street_count} streets.")

    # Shuffle street records for randomness
    random.shuffle(street_rows)

    total_updated = 0
    batch_number = 1

    # Process incidents in batches
    for i in range(0, incident_count, batch_size):
        batch_ids = incident_ids[i:i+batch_size]

        for j, ir_id in enumerate(batch_ids):
            # Cycle through street records if incidents > streets
            street = street_rows[(i + j) % street_count]

            update_sql = f"""
            UPDATE {config.TABLE_NAME}
            SET Str_name = %s,
                Suburb = %s,
                Town = %s,
                City = %s,
                Latitude = %s,
                Longitude = %s,
                X_Road = %s,
                Primary_Station = %s,
                Region_ID = %s,
                Region = %s
            WHERE id = %s
            """
            cursor.execute(update_sql, (
                street["Main_Road"],
                street["Suburb"],
                street["Town"],
                street["City"],
                street["XRoad_Latitude"],
                street["XRoad_Longitude"],
                street["X_Road"],
                street["Fire_Station"],
                street["Region_ID"],
                street["Region_Name"],
                ir_id
            ))
            total_updated += cursor.rowcount

        print(f"✅ Batch {batch_number} completed: {len(batch_ids)} rows updated")
        batch_number += 1

    cursor.close()
    conn.close()
    print(f"🎯 All batches done. Total rows updated: {total_updated} (expected {incident_count})")

if __name__ == "__main__":
    update_random_streets(batch_size=300)