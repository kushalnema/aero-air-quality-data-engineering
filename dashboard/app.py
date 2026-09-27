import streamlit as st
import pandas as pd


st.set_page_config(
    page_title="Air Quality Dashboard",
    page_icon="🌍",
    layout="wide",
)


st.title("🌍 Indian Air Quality Dashboard")
st.write("Air-quality station and measurement data loaded from TiDB Cloud.")


# --------------------------------------------------
# TiDB Cloud connection
# --------------------------------------------------

conn = st.connection(
    "tidb",
    type="sql"
)


# --------------------------------------------------
# Load station data
# --------------------------------------------------

station_query = """
SELECT
    id,
    name,
    locality,
    country_code,
    latitude,
    longitude
FROM air_quality_locations
"""

stations_df = conn.query(
    station_query,
    ttl=600
)


# --------------------------------------------------
# Load measurement data
# --------------------------------------------------

measurement_query = """
SELECT
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
FROM fact_air_quality_measurements
ORDER BY measurement_time_utc DESC
"""

measurements_df = conn.query(
    measurement_query,
    ttl=600
)


# --------------------------------------------------
# Dashboard metrics
# --------------------------------------------------

col1, col2, col3, col4 = st.columns(4)


with col1:
    st.metric(
        "Total Stations",
        len(stations_df)
    )


with col2:
    st.metric(
        "Locations",
        stations_df["locality"].nunique()
    )


with col3:
    st.metric(
        "Countries",
        stations_df["country_code"].nunique()
    )


with col4:
    if not measurements_df.empty:

        latest_value = measurements_df.iloc[0][
            "measurement_value"
        ]

        latest_unit = measurements_df.iloc[0][
            "unit"
        ]

        st.metric(
            "Latest PM2.5",
            f"{latest_value} {latest_unit}"
        )

    else:
        st.metric(
            "Latest PM2.5",
            "N/A"
        )


# --------------------------------------------------
# Measurements
# --------------------------------------------------

st.subheader("📊 Air Quality Measurements")


if measurements_df.empty:

    st.info(
        "No air-quality measurements available."
    )

else:

    display_columns = [
        "sensor_id",
        "location_id",
        "parameter_display_name",
        "measurement_value",
        "unit",
        "measurement_time_local",
    ]

    st.dataframe(
        measurements_df[display_columns],
        use_container_width=True,
    )


# --------------------------------------------------
# Stations
# --------------------------------------------------

st.subheader("📍 Air Quality Stations")

st.dataframe(
    stations_df,
    use_container_width=True,
)


# --------------------------------------------------
# Map
# --------------------------------------------------

st.subheader("🗺️ Station Map")

map_data = stations_df[
    ["latitude", "longitude"]
].dropna()

st.map(map_data)