from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator


with DAG(
    dag_id="air_quality_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["air-quality", "data-engineering"],
) as dag:

    # ----------------------------------------------
    # Location pipeline
    # ----------------------------------------------

    ingest_locations = BashOperator(
        task_id="ingest_locations",
        bash_command="""
        cd /opt/airflow/project &&
        python src/ingestion/fetch_air_quality.py
        """,
    )

    transform_locations = BashOperator(
        task_id="transform_locations",
        bash_command="""
        cd /opt/airflow/project &&
        python src/transformation/clean_air_quality.py
        """,
    )

    # ----------------------------------------------
    # Measurement ingestion
    # ----------------------------------------------

    ingest_measurements = BashOperator(
        task_id="ingest_measurements",
        bash_command="""
        cd /opt/airflow/project &&
        python src/ingestion/fetch_measurements.py
        """,
    )

    transform_measurements = BashOperator(
        task_id="transform_measurements",
        bash_command="""
        cd /opt/airflow/project &&
        python src/transformation/clean_measurements.py
        """,
    )

    # ----------------------------------------------
    # Data quality
    # ----------------------------------------------

    validate_data = BashOperator(
        task_id="validate_data",
        bash_command="""
        cd /opt/airflow/project &&
        pytest -q
        """,
    )

    # ----------------------------------------------
    # Load Gold
    # ----------------------------------------------

    load_locations = BashOperator(
        task_id="load_locations",
        bash_command="""
        cd /opt/airflow/project &&
        python src/load/load_to_mysql.py
        """,
    )

    load_measurements = BashOperator(
        task_id="load_measurements",
        bash_command="""
        cd /opt/airflow/project &&
        python src/load/load_measurements_to_mysql.py
        """,
    )

    # ----------------------------------------------
    # Dependencies
    # ----------------------------------------------

    ingest_locations >> transform_locations

    ingest_measurements >> transform_measurements

    [
        transform_locations,
        transform_measurements,
    ] >> validate_data

    validate_data >> [
        load_locations,
        load_measurements,
    ]