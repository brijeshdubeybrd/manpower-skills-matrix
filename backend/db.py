import os
from google.cloud import bigquery
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# BigQuery Configuration
# REPLACE THESE WITH YOUR ACTUAL VALUES or set them as environment variables
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "raymond-data-lake")
DATASET_ID = os.getenv("BIGQUERY_DATASET_ID", "manpower_skills_matrix")
TABLE_ID = os.getenv("BIGQUERY_TABLE_ID", "manpower_skills_matrix") # Assuming table name is 'manpower'

class BigQueryClient:
    def __init__(self):
        try:
            self.client = bigquery.Client(project=PROJECT_ID)
            self.table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
            logger.info(f"BigQuery Client initialized for {self.table_ref}")
        except Exception as e:
            logger.error(f"Failed to initialize BigQuery Client: {e}")
            self.client = None

    def get_manpower_data(self) -> List[Dict[str, Any]]:
        if not self.client:
            logger.warning("BigQuery client not initialized. Returning empty list.")
            return []

        query = f"SELECT * FROM `{self.table_ref}`"
        try:
            query_job = self.client.query(query)
            results = query_job.result()  # Waits for job to complete.
            
            data = []
            for row in results:
                # Convert Row to dict
                record = dict(row)
                data.append(record)
            
            logger.info(f"Fetched {len(data)} records from BigQuery")
            return data
        except Exception as e:
            logger.error(f"Error fetching data from BigQuery: {e}")
            return []

    # Note: BigQuery is not optimized for single-record updates/deletes.
    # DML operations have quotas and latency.
    # For this implementation, we will log warnings for write operations.
    
    def update_record(self, record_id: int, updated_data: Dict[str, Any]) -> bool:
        # Placeholder for update logic
        # Implementation depends on table schema and partitioning
        logger.warning(f"Update requested for id {record_id}. BigQuery updates are expensive and not implemented in this demo.")
        return False

    def delete_record(self, record_id: int) -> bool:
         # Placeholder for delete logic
        logger.warning(f"Delete requested for id {record_id}. BigQuery deletes are expensive and not implemented in this demo.")
        return False

# Global instance
bq_client = BigQueryClient()
