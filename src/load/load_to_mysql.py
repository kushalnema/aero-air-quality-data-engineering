import os
from pathlib import Path

import mysql.connector
import pandas as pd
from dotenv import load_dotenv


# --------------------------------------------------
# Configuration
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(
    PROJECT_ROOT / ".env"
)


SILVER_FILE = (
    PROJECT_ROOT
    / "data"
    / "silver"
    / "air_quality_clean.csv"
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


# --------------------------------------------------
# Validate configuration
# --------------------------------------------------

required_values = {
    "MYSQL_USER": MYSQL_USER,
    "MYSQL_PASSWORD": MYSQL_PASSWORD,
    "MYSQL_DATABASE": MYSQL_DATABASE
}


for name, value in required_values.items():

    if not value:

        raise ValueError(
            f"{name} is missing from .env"
        )


# --------------------------------------------------
# Check Silver
# --------------------------------------------------

if not SILVER_FILE.exists():

    raise FileNotFoundError(
        f"Silver file not found: {SILVER_FILE}"
    )


# --------------------------------------------------
# Connect to MySQL
# --------------------------------------------------

connection = mysql.connector.connect(
    host=MYSQL_HOST,
    port=MYSQL_PORT,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DATABASE
)

cursor = connection.cursor()

print(
    "Connected to MySQL successfully!"
)


# --------------------------------------------------
# Read Silver
# --------------------------------------------------

df = pd.read_csv(
    SILVER_FILE
)

print(
    f"Silver records: {len(df)}"
)


# --------------------------------------------------
# Create Gold table
# --------------------------------------------------

create_table_query = """

CREATE TABLE IF NOT EXISTS air_quality_locations (

    id INT PRIMARY KEY,

    name VARCHAR(255),

    locality VARCHAR(255),

    country_code VARCHAR(10),

    latitude DOUBLE,

    longitude DOUBLE

)

"""

cursor.execute(
    create_table_query
)


# --------------------------------------------------
# Insert data
# --------------------------------------------------

insert_query = """

INSERT INTO air_quality_locations
(
    id,
    name,
    locality,
    country_code,
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
    %s
)

ON DUPLICATE KEY UPDATE

    name = VALUES(name),

    locality = VALUES(locality),

    country_code = VALUES(country_code),

    latitude = VALUES(latitude),

    longitude = VALUES(longitude)

"""


records_loaded = 0


for _, row in df.iterrows():

    cursor.execute(
        insert_query,
        (
            row.get("id"),
            row.get("name"),
            row.get("locality"),
            row.get("country_code"),
            row.get("coordinates_latitude"),
            row.get("coordinates_longitude"),
        )
    )

    records_loaded += 1


# --------------------------------------------------
# Commit
# --------------------------------------------------

connection.commit()

print(
    f"Gold records loaded: {records_loaded}"
)


# --------------------------------------------------
# Close connection
# --------------------------------------------------

cursor.close()

connection.close()

print(
    "MySQL connection closed."
)

print(
    "Gold load completed successfully!"
)