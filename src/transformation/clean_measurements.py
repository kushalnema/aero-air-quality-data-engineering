from pathlib import Path

import pandas as pd


# ==================================================
# PROJECT PATHS
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

BRONZE_DIR = (
    PROJECT_ROOT
    / "data"
    / "bronze"
)

SILVER_DIR = (
    PROJECT_ROOT
    / "data"
    / "silver"
)

BRONZE_FILE = (
    BRONZE_DIR
    / "air_quality_measurements.csv"
)

SILVER_FILE = (
    SILVER_DIR
    / "air_quality_measurements_clean.csv"
)


# ==================================================
# CHECK BRONZE FILE
# ==================================================

if not BRONZE_FILE.exists():
    raise FileNotFoundError(
        f"Bronze file not found: {BRONZE_FILE}"
    )


# ==================================================
# READ BRONZE DATA
# ==================================================

df = pd.read_csv(BRONZE_FILE)

print(
    f"Bronze measurements: {len(df)}"
)

print("\nBronze columns:")

print(
    df.columns.tolist()
)


# ==================================================
# REMOVE DUPLICATES
# ==================================================

before_count = len(df)

df = df.drop_duplicates().copy()

after_count = len(df)

print(
    f"\nDuplicates removed: "
    f"{before_count - after_count}"
)


# ==================================================
# RENAME COLUMNS
# ==================================================

df = df.rename(
    columns={
        "value": "measurement_value",
        "sensorsId": "sensor_id",
        "locationsId": "location_id",
        "datetime.utc": "measurement_time_utc",
        "datetime.local": "measurement_time_local",
        "coordinates.latitude": "latitude",
        "coordinates.longitude": "longitude",
    }
)


# ==================================================
# CHECK REQUIRED COLUMNS
# ==================================================

required_columns = [
    "measurement_value",
    "sensor_id",
    "location_id",
    "measurement_time_utc",
    "measurement_time_local",
    "latitude",
    "longitude",
    "parameter",
    "parameter_display_name",
    "unit",
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        "Missing required columns: "
        f"{missing_columns}"
    )


# ==================================================
# CONVERT TIMESTAMPS
# ==================================================

df["measurement_time_utc"] = pd.to_datetime(
    df["measurement_time_utc"],
    utc=True
)

df["measurement_time_local"] = pd.to_datetime(
    df["measurement_time_local"]
)


# ==================================================
# CONVERT NUMERIC COLUMNS
# ==================================================

numeric_columns = [
    "measurement_value",
    "sensor_id",
    "location_id",
    "latitude",
    "longitude",
]

for column in numeric_columns:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


# ==================================================
# CLEAN TEXT COLUMNS
# ==================================================

text_columns = [
    "parameter",
    "parameter_display_name",
    "unit",
]

for column in text_columns:

    df[column] = (
        df[column]
        .astype("string")
        .str.strip()
    )


# ==================================================
# REMOVE INVALID RECORDS
# ==================================================

df = df.dropna(
    subset=[
        "measurement_value",
        "sensor_id",
        "location_id",
        "measurement_time_utc",
        "parameter",
        "unit",
    ]
)


# ==================================================
# CREATE SILVER DIRECTORY
# ==================================================

SILVER_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==================================================
# SAVE SILVER DATA
# ==================================================

df.to_csv(
    SILVER_FILE,
    index=False
)


# ==================================================
# DISPLAY RESULTS
# ==================================================

print(
    f"\nSilver measurements: {len(df)}"
)

print(
    f"Silver data saved to: "
    f"{SILVER_FILE}"
)

print("\nSilver columns:")

print(
    df.columns.tolist()
)

print("\nSilver data:")

print(
    df.to_string(index=False)
)