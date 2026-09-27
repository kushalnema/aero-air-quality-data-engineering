from pathlib import Path

import pandas as pd


# --------------------------------------------------
# Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

BRONZE_DIR = PROJECT_ROOT / "data" / "bronze"

SILVER_DIR = PROJECT_ROOT / "data" / "silver"

BRONZE_FILE = (
    BRONZE_DIR / "openaq_locations.csv"
)

SILVER_FILE = (
    SILVER_DIR / "air_quality_clean.csv"
)


# --------------------------------------------------
# Check Bronze file
# --------------------------------------------------

if not BRONZE_FILE.exists():

    raise FileNotFoundError(
        f"Bronze file not found: {BRONZE_FILE}"
    )


# --------------------------------------------------
# Read Bronze
# --------------------------------------------------

df = pd.read_csv(
    BRONZE_FILE
)

print(
    f"Bronze records: {len(df)}"
)


# --------------------------------------------------
# Remove duplicates
# --------------------------------------------------

before_count = len(df)

df = df.drop_duplicates().copy()

after_count = len(df)

print(
    f"Duplicates removed: "
    f"{before_count - after_count}"
)


# --------------------------------------------------
# Standardize column names
# --------------------------------------------------

df.columns = (
    df.columns
    .astype(str)
    .str.strip()
    .str.lower()
    .str.replace(
        ".",
        "_",
        regex=False
    )
)


# --------------------------------------------------
# Clean text columns
# --------------------------------------------------

text_columns = df.select_dtypes(
    include=["object"]
).columns

for column in text_columns:

    df[column] = (
        df[column]
        .astype("string")
        .str.strip()
    )


# --------------------------------------------------
# Create Silver directory
# --------------------------------------------------

SILVER_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# --------------------------------------------------
# Save Silver
# --------------------------------------------------

df.to_csv(
    SILVER_FILE,
    index=False
)

print(
    f"Silver records: {len(df)}"
)

print(
    f"Silver data saved to: {SILVER_FILE}"
)