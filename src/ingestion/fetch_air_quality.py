import json
import os
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv


# --------------------------------------------------
# Configuration
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

BRONZE_DIR = PROJECT_ROOT / "data" / "bronze"

load_dotenv(PROJECT_ROOT / ".env")

API_KEY = os.getenv("OPENAQ_API_KEY")

if not API_KEY:
    raise ValueError("OPENAQ_API_KEY not found in .env")


# --------------------------------------------------
# OpenAQ API
# --------------------------------------------------

URL = "https://api.openaq.org/v3/locations/8118"

HEADERS = {
    "X-API-Key": API_KEY
}


# --------------------------------------------------
# Request data
# --------------------------------------------------

print("Fetching data from OpenAQ...")

response = requests.get(
    URL,
    headers=HEADERS,
    timeout=30
)

response.raise_for_status()

data = response.json()

print("API request successful!")


# --------------------------------------------------
# Create Bronze directory
# --------------------------------------------------

BRONZE_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# --------------------------------------------------
# Save raw JSON
# --------------------------------------------------

raw_file = BRONZE_DIR / "openaq_raw.json"

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

print(f"Raw JSON saved to: {raw_file}")


# --------------------------------------------------
# Convert JSON to DataFrame
# --------------------------------------------------

if "results" not in data:

    raise ValueError(
        "API response does not contain 'results'"
    )


df = pd.json_normalize(
    data["results"]
)

print(
    f"Records received: {len(df)}"
)


# --------------------------------------------------
# Save Bronze CSV
# --------------------------------------------------

csv_file = BRONZE_DIR / "openaq_locations.csv"

df.to_csv(
    csv_file,
    index=False
)

print(
    f"Bronze CSV saved to: {csv_file}"
)

print("\nColumns:")
print(df.columns.tolist())