import os
from pathlib import Path

import mysql.connector
import pandas as pd
from dotenv import load_dotenv


# ==================================================
# PROJECT PATHS
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SILVER_FILE = (
    PROJECT_ROOT
    / "data"
    / "silver"
    / "air_quality_measurements_clean.csv"
)


# ==================================================
# LOAD ENVIRONMENT VARIABLES
# ==================================================

load_dotenv(
    PROJECT_ROOT / ".env"
)

MYSQL_HOST = os.getenv(
    "MYSQL_HOST",
    "localhost"
)

MYSQL_PORT = int(
    os.getenv(
        "MYSQL_PORT",
        "3306"
    )
)

MYSQL_USER = os.getenv(
    "MYSQL_USER"
)

MYSQL_PASSWORD = os.getenv(
    "MYSQL_PASSWORD"
)

MYSQL_DATABASE = os.getenv(
    "MYSQL_DATABASE"
)


# ==================================================
# VALIDATE CONFIGURATION
# ==================================================

required_values = {
    "MYSQL_USER": MYSQL_USER,
    "MYSQL_PASSWORD": MYSQL_PASSWORD,
    "MYSQL_DATABASE": MYSQL_DATABASE,
}

for name, value in required_values.items():

    if not value:
        raise ValueError(
            f"{name} is missing from .env"
        )


# ==================================================
# CHECK SILVER FILE
# ==================================================

if not SILVER_FILE.exists():

    raise FileNotFoundError(
        f"Silver file not found: {SILVER_FILE}"
    )


# ==================================================
# READ SILVER DATA
# ==================================================

df = pd.read_csv(
    SILVER_FILE
)

print(
    f"Silver measurements: {len(df)}"
)

print("\nSilver columns:")

print(
    df.columns.tolist()
)


# ==================================================
# CONNECT TO MYSQL
# ==================================================

connection = mysql.connector.connect(
    host=MYSQL_HOST,
    port=MYSQL_PORT,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DATABASE,
)

cursor = connection.cursor()

print(
    "\nConnected to MySQL successfully!"
)


# ==================================================
# CREATE GOLD TABLE
# ==================================================

create_table_query = """
CREATE TABLE IF NOT EXISTS fact_air_quality_measurements (

    measurement_id BIGINT AUTO_INCREMENT PRIMARY KEY,

    sensor_id INT NOT NULL,

    location_id INT NOT NULL,

    parameter VARCHAR(50) NOT NULL,

    parameter_display_name VARCHAR(100),

    measurement_value DOUBLE NOT NULL,

    unit VARCHAR(50) NOT NULL,

    measurement_time_utc DATETIME NOT NULL,

    measurement_time_local DATETIME,

    latitude DOUBLE,

    longitude DOUBLE,

    UNIQUE KEY unique_measurement (
        sensor_id,
        measurement_time_utc
    )
)
"""

cursor.execute(
    create_table_query
)

print(
    "Gold measurement table ready!"
)


# ==================================================
# INSERT QUERY
# ==================================================

insert_query = """
INSERT INTO fact_air_quality_measurements
(
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
VALUES
(
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s
)

ON DUPLICATE KEY UPDATE

    measurement_value = VALUES(
        measurement_value
    ),

    parameter = VALUES(
        parameter
    ),

    parameter_display_name = VALUES(
        parameter_display_name
    ),

    unit = VALUES(
        unit
    ),

    measurement_time_local = VALUES(
        measurement_time_local
    ),

    latitude = VALUES(
        latitude
    ),

    longitude = VALUES(
        longitude
    )
"""


# ==================================================
# LOAD RECORDS
# ==================================================

records_loaded = 0

for _, row in df.iterrows():

    cursor.execute(
        insert_query,
        (
            int(row["sensor_id"]),

            int(row["location_id"]),

            row["parameter"],

            row["parameter_display_name"],

            float(
                row["measurement_value"]
            ),

            row["unit"],

            pd.to_datetime(
                row["measurement_time_utc"]
            ).to_pydatetime(),

            pd.to_datetime(
                row["measurement_time_local"]
            ).to_pydatetime(),

            float(row["latitude"])
            if pd.notna(row["latitude"])
            else None,

            float(row["longitude"])
            if pd.notna(row["longitude"])
            else None,
        )
    )

    records_loaded += 1


# ==================================================
# COMMIT TRANSACTION
# ==================================================

connection.commit()

print(
    f"Records loaded: {records_loaded}"
)


# ==================================================
# CLOSE CONNECTION
# ==================================================

cursor.close()

connection.close()

print(
    "MySQL connection closed."
)

print(
    "Gold measurement load completed successfully!"
)