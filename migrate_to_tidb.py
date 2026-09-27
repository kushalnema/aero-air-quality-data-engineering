import os
from pathlib import Path

import mysql.connector
import pandas as pd
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent

load_dotenv(PROJECT_ROOT / ".env")


# --------------------------------------------------
# 1. Connect to LOCAL MySQL
# --------------------------------------------------

local_connection = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST", "localhost"),
    port=int(os.getenv("MYSQL_PORT", "3306")),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DATABASE"),
)

print("Connected to local MySQL!")

# Read locations
locations_df = pd.read_sql(
    "SELECT * FROM air_quality_locations",
    local_connection,
)

# Read measurements
measurements_df = pd.read_sql(
    "SELECT * FROM fact_air_quality_measurements",
    local_connection,
)

local_connection.close()

print(f"Local locations: {len(locations_df)}")
print(f"Local measurements: {len(measurements_df)}")


# --------------------------------------------------
# 2. Connect to TiDB Cloud
# --------------------------------------------------

tidb_connection = mysql.connector.connect(
    host=os.getenv("TIDB_HOST"),
    port=int(os.getenv("TIDB_PORT", "4000")),
    user=os.getenv("TIDB_USER"),
    password=os.getenv("TIDB_PASSWORD"),
    database=os.getenv("TIDB_DATABASE"),
    ssl_ca=str(PROJECT_ROOT / os.getenv("TIDB_CA_PATH")),
    ssl_verify_cert=True,
    ssl_verify_identity=True,
)

print("Connected to TiDB Cloud!")


# --------------------------------------------------
# 3. Load locations
# --------------------------------------------------

cursor = tidb_connection.cursor()

location_query = """
INSERT INTO air_quality_locations
(
    id,
    name,
    locality,
    country_code,
    latitude,
    longitude
)
VALUES (%s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    locality = VALUES(locality),
    country_code = VALUES(country_code),
    latitude = VALUES(latitude),
    longitude = VALUES(longitude)
"""

location_records = [
    (
        row["id"],
        row["name"],
        row["locality"],
        row["country_code"],
        row["latitude"],
        row["longitude"],
    )
    for _, row in locations_df.iterrows()
]

cursor.executemany(location_query, location_records)

print(f"Loaded locations into TiDB: {cursor.rowcount}")


# --------------------------------------------------
# 4. Load measurements
# --------------------------------------------------

measurement_query = """
INSERT INTO fact_air_quality_measurements
(
    measurement_id,
    sensor_id,
    location_id,
    parameter,
    parameter_display_name,
    measurement_value,
    unit,
    measurement_time_utc,
    measurement_time_local,
    latitude,
    longitude
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    sensor_id = VALUES(sensor_id),
    location_id = VALUES(location_id),
    parameter = VALUES(parameter),
    parameter_display_name = VALUES(parameter_display_name),
    measurement_value = VALUES(measurement_value),
    unit = VALUES(unit),
    measurement_time_utc = VALUES(measurement_time_utc),
    measurement_time_local = VALUES(measurement_time_local),
    latitude = VALUES(latitude),
    longitude = VALUES(longitude)
"""

measurement_records = [
    (
        row["measurement_id"],
        row["sensor_id"],
        row["location_id"],
        row["parameter"],
        row["parameter_display_name"],
        row["measurement_value"],
        row["unit"],
        row["measurement_time_utc"],
        row["measurement_time_local"],
        row["latitude"],
        row["longitude"],
    )
    for _, row in measurements_df.iterrows()
]

cursor.executemany(measurement_query, measurement_records)

print(f"Loaded measurements into TiDB: {cursor.rowcount}")


# --------------------------------------------------
# 5. Commit
# --------------------------------------------------

tidb_connection.commit()

cursor.close()
tidb_connection.close()

print("\nMigration completed successfully!")