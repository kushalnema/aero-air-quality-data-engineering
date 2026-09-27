import json
import os
from pathlib import Path

import pandas as pd
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
# OpenAQ configuration
# --------------------------------------------------

LOCATION_ID = 8118

URL = (
    f"https://api.openaq.org/v3/"
    f"locations/{LOCATION_ID}/latest"
)

HEADERS = {
    "X-API-Key": API_KEY
}


# --------------------------------------------------
# Fetch latest measurements
# --------------------------------------------------

print("Fetching latest air-quality measurements...")

response = requests.get(
    URL,
    headers=HEADERS,
    params={"limit": 100},
    timeout=30
)

response.raise_for_status()

data = response.json()

print("API request successful!")


# --------------------------------------------------
# Validate API response
# --------------------------------------------------

if "results" not in data:
    raise ValueError(
        "API response does not contain 'results'"
    )


# --------------------------------------------------
# Save raw response
# --------------------------------------------------

BRONZE_DIR.mkdir(
    parents=True,
    exist_ok=True
)

raw_file = (
    BRONZE_DIR
    / "measurements_raw.json"
)

with open(
    raw_file,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        data,
        file,
        indent=2
    )

print(
    f"Raw measurements saved to: {raw_file}"
)


# --------------------------------------------------
# Convert JSON to DataFrame
# --------------------------------------------------

df = pd.json_normalize(
    data["results"]
)

print(
    f"Measurements received: {len(df)}"
)


# --------------------------------------------------
# Add sensor metadata
# --------------------------------------------------

SENSOR_ID = 23534

SENSOR_URL = (
    f"https://api.openaq.org/v3/"
    f"sensors/{SENSOR_ID}"
)

sensor_response = requests.get(
    SENSOR_URL,
    headers=HEADERS,
    timeout=30
)

sensor_response.raise_for_status()

sensor_data = sensor_response.json()

sensor_results = sensor_data.get(
    "results",
    []
)

if not sensor_results:
    raise ValueError(
        "Sensor information not found"
    )

sensor = sensor_results[0]

parameter = sensor["parameter"]

df["parameter"] = parameter["name"]

df["parameter_display_name"] = (
    parameter["displayName"]
)

df["unit"] = parameter["units"]


# --------------------------------------------------
# Save Bronze CSV
# --------------------------------------------------

csv_file = (
    BRONZE_DIR
    / "air_quality_measurements.csv"
)

df.to_csv(
    csv_file,
    index=False
)

print(
    f"Measurements saved to: {csv_file}"
)


# --------------------------------------------------
# Display information
# --------------------------------------------------

print("\nColumns:")

print(
    df.columns.tolist()
)

print("\nMeasurement data:")

print(
    df.to_string(index=False)
)