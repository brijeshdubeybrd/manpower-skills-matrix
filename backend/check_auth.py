from google.cloud import bigquery
import os

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "raymond-data-lake")

print(f"Attempting to connect to project: {PROJECT_ID}")
print(f"GOOGLE_APPLICATION_CREDENTIALS: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')}")

try:
    client = bigquery.Client(project=PROJECT_ID)
    print("Successfully initialized BigQuery Client")
    print(f"Project: {client.project}")
    
    # Try a simple API call to verify perms
    datasets = list(client.list_datasets())
    print(f"Datasets found: {[d.dataset_id for d in datasets]}")
    
except Exception as e:
    print("FAILED to initialize/use BigQuery Client.")
    print(f"Error type: {type(e)}")
    print(f"Error message: {e}")
    # import traceback
    # traceback.print_exc()
