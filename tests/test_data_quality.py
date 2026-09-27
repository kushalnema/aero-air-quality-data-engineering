from pathlib import Path

import pandas as pd
import pytest


# ==================================================
# PROJECT PATHS
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]


# ==================================================
# LOCATION SILVER FILE
# ==================================================

SILVER_FILE = (
    PROJECT_ROOT
    / "data"
    / "silver"
    / "air_quality_clean.csv"
)


# ==================================================
# MEASUREMENT SILVER FILE
# ==================================================

MEASUREMENTS_SILVER_FILE = (
    PROJECT_ROOT
    / "data"
    / "silver"
    / "air_quality_measurements_clean.csv"
)


# ==================================================
# LOCATION DATA FIXTURE
# ==================================================

@pytest.fixture
def df():
    """
    Load cleaned location data from the Silver layer.
    """
    return pd.read_csv(SILVER_FILE)


# ==================================================
# LOCATION DATA TESTS
# ==================================================

def test_silver_file_exists():
    """
    Verify that the location Silver file exists.
    """
    assert SILVER_FILE.exists()


def test_data_is_not_empty(df):
    """
    Verify that location data contains records.
    """
    assert len(df) > 0


def test_no_duplicate_records(df):
    """
    Verify that location data contains no duplicate rows.
    """
    assert df.duplicated().sum() == 0


def test_station_id_exists(df):
    """
    Verify that station ID exists.
    """
    assert "id" in df.columns


def test_coordinates_exist(df):
    """
    Verify that latitude and longitude columns exist.
    """
    assert "coordinates_latitude" in df.columns
    assert "coordinates_longitude" in df.columns


# ==================================================
# MEASUREMENT DATA FIXTURE
# ==================================================

@pytest.fixture
def measurements_df():
    """
    Load cleaned measurement data from the Silver layer.
    """
    return pd.read_csv(MEASUREMENTS_SILVER_FILE)


# ==================================================
# MEASUREMENT FILE TESTS
# ==================================================

def test_measurements_file_exists():
    """
    Verify that the measurement Silver file exists.
    """
    assert MEASUREMENTS_SILVER_FILE.exists()


def test_measurements_are_not_empty(measurements_df):
    """
    Verify that measurement data contains records.
    """
    assert len(measurements_df) > 0


def test_measurements_have_no_duplicates(measurements_df):
    """
    Verify that measurement data contains no duplicate rows.
    """
    assert measurements_df.duplicated().sum() == 0


# ==================================================
# REQUIRED MEASUREMENT COLUMNS
# ==================================================

def test_measurement_columns_exist(measurements_df):
    """
    Verify that all required measurement columns exist.
    """

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

    for column in required_columns:
        assert column in measurements_df.columns


# ==================================================
# MEASUREMENT VALUE TESTS
# ==================================================

def test_measurement_values_are_numeric(measurements_df):
    """
    Verify that measurement values are numeric.
    """
    assert pd.api.types.is_numeric_dtype(
        measurements_df["measurement_value"]
    )


def test_measurement_values_are_not_null(measurements_df):
    """
    Verify that measurement values are not NULL.
    """
    assert measurements_df["measurement_value"].notna().all()


# ==================================================
# SENSOR TESTS
# ==================================================

def test_sensor_ids_are_numeric(measurements_df):
    """
    Verify that sensor IDs are numeric.
    """
    assert pd.api.types.is_numeric_dtype(
        measurements_df["sensor_id"]
    )


def test_sensor_ids_are_not_null(measurements_df):
    """
    Verify that sensor IDs are not NULL.
    """
    assert measurements_df["sensor_id"].notna().all()


# ==================================================
# LOCATION TESTS
# ==================================================

def test_location_ids_are_numeric(measurements_df):
    """
    Verify that location IDs are numeric.
    """
    assert pd.api.types.is_numeric_dtype(
        measurements_df["location_id"]
    )


def test_location_ids_are_not_null(measurements_df):
    """
    Verify that location IDs are not NULL.
    """
    assert measurements_df["location_id"].notna().all()


# ==================================================
# COORDINATE TESTS
# ==================================================

def test_coordinates_are_numeric(measurements_df):
    """
    Verify that latitude and longitude are numeric.
    """
    assert pd.api.types.is_numeric_dtype(
        measurements_df["latitude"]
    )

    assert pd.api.types.is_numeric_dtype(
        measurements_df["longitude"]
    )


# ==================================================
# PARAMETER TESTS
# ==================================================

def test_parameter_exists(measurements_df):
    """
    Verify that the pollutant parameter exists.
    """
    assert "parameter" in measurements_df.columns


def test_parameter_display_name_exists(measurements_df):
    """
    Verify that the parameter display name exists.
    """
    assert "parameter_display_name" in measurements_df.columns


def test_parameter_is_not_null(measurements_df):
    """
    Verify that parameter values are not NULL.
    """
    assert measurements_df["parameter"].notna().all()


def test_parameter_display_name_is_not_null(measurements_df):
    """
    Verify that parameter display names are not NULL.
    """
    assert measurements_df[
        "parameter_display_name"
    ].notna().all()


# ==================================================
# UNIT TESTS
# ==================================================

def test_unit_exists(measurements_df):
    """
    Verify that the unit column exists.
    """
    assert "unit" in measurements_df.columns


def test_unit_is_not_null(measurements_df):
    """
    Verify that measurement units are not NULL.
    """
    assert measurements_df["unit"].notna().all()