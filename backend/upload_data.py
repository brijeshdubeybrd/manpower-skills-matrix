import json
import os
from google.cloud import bigquery
from db import bq_client, TABLE_ID, DATASET_ID, PROJECT_ID

DATA_FILE = "mock_db.json"

def upload_data():
    if not os.path.exists(DATA_FILE):
        print(f"Error: {DATA_FILE} not found!")
        return

    print(f"Reading data from {DATA_FILE}...")
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not data:
        print("No data found in mock_db.json")
        return

    client = bq_client.client
    if not client:
        print("BigQuery client is not initialized. Check your credentials.")
        return

    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    print(f"Uploading {len(data)} records to {table_ref}...")

    job_config = bigquery.LoadJobConfig(
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE, # Overwrite table
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    )

    try:
        job = client.load_table_from_json(data, table_ref, job_config=job_config)
        job.result()  # Waits for the job to complete.
        print(f"Loaded {job.output_rows} rows into {table_ref}.")
    except Exception as e:
        print(f"Failed to upload data: {e}")

if __name__ == "__main__":
    upload_data()
