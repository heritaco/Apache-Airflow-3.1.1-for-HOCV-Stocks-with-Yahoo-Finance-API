"""
DAG to scan and ingest new Muestra Excel files.
It checks for new files in the specified directory,
processes them, and updates the PostgreSQL database accordingly.

Scan `/opt/airflow/data/muestra` for `Muestra_YYMMDD.xlsx`.

- Only process files not present in `muestra.files_processed`.
- For each file:
  - Fill `muestra.identity` and `muestra.index_membership`
  - Create/update one table `muestra.<ticker>` per ticker (NVDA, etc.).
"""

from __future__ import annotations

import os
import re
from datetime import datetime, timedelta, timezone

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

from plugins.muestra_shared import scan_and_ingest_new_files

default_args = {
    "owner": "heri",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="07_04_muestra_ingest_new_files_v3",
    start_date=datetime(2025, 11, 10),
    schedule="*/5 * * * *",   # every 5 minutes, adjust if you like
    catchup=False,
    max_active_runs=1,
    dagrun_timeout=timedelta(minutes=20),
    default_args=default_args,
    tags=["muestra", "excel", "file-driven"],
    description=__doc__,
) as dag:

    scan_and_ingest = PythonOperator(
        task_id="scan_and_ingest_new_files",
        python_callable=scan_and_ingest_new_files,
        op_kwargs={
            "data_dir": "/opt/airflow/data/muestra",
            "postgres_conn_id": "postgres_default",
            "database": "airflow",
        },
    )
