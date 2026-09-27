import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv


# --------------------------------------------------
# Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

BRONZE_DIR = (
    PROJECT_ROOT
    / "data"
    / "bronze"
)


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv(PROJECT_ROOT / ".env")

API_KEY = os.getenv("OPENAQ_API_KEY")

if not API_KEY:
    raise ValueError(
        "OPENAQ_API_KEY not found in .env"
    )


# --------------------------------------------------
# Sensor information
# --------------------------------------------------

SENSOR_ID = 23534

URL = f"https://api.openaq.org/v3/sensors/{SENSOR_ID}"

HEADERS = {
    "X-API-Key": API_KEY
}


# --------------------------------------------------
# API request
# --------------------------------------------------

print(
    f"Fetching sensor information for "
    f"sensor {SENSOR_ID}..."
)

response = requests.get(
    URL,
    headers=HEADERS,
    timeout=30
)

response.raise_for_status()

data = response.json()

print("API request successful!")


# --------------------------------------------------
# Save raw sensor information
# --------------------------------------------------

BRONZE_DIR.mkdir(
    parents=True,
    exist_ok=True
)

output_file = (
    BRONZE_DIR
    / "sensor_23534_raw.json"
)

with open(
    output_file,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        data,
        file,
        indent=2
    )


print(
    f"Sensor data saved to: "
    f"{output_file}"
)


# --------------------------------------------------
# Display response
# --------------------------------------------------

print("\nSensor response:")

print(
    json.dumps(
        data,
        indent=2
    )
)