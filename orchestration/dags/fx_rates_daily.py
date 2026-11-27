from datetime import datetime, timedelta
from pathlib import Path

from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import dag
from libs.fx_client import get_daily_rates
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.sdk import dag, task

GCS_BUCKET = "payments-data-platform-pz01126-raw"


@dag(
    dag_id="fx_rates_daily",
    start_date=datetime(2026, 11, 10),
    schedule=None,
    catchup=False,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=1),
    },
    tags=["Currency rate fetch", "Save to GC bucket"],
)
def fx_rates_daily():
    
    @task
    def extract_rates(ds: str) -> str:
        return get_daily_rates(ds,"gbp,usd", "ecb")

    @task
    def load_to_gcs(
        input_file: str,
        ds: str,
        bucket_name: str = GCS_BUCKET,
    ) -> str:
        """Uploads the local JSON file to GCS, cleans it up, and returns the gs:// URI."""
        local_path = Path(input_file)
        object_name = f"fx/dt={ds}/fx_rates.json"

        hook = GCSHook(gcp_conn_id="google_cloud_default")
        hook.upload(
            bucket_name=bucket_name,
            object_name=object_name,
            filename=str(local_path),
            mime_type="application/json",
        )
        
        local_path.unlink(missing_ok=True)
        return f"gs://{bucket_name}/{object_name}"

    json_file_path = extract_rates()
    load_to_gcs(input_file=json_file_path)

fx_rates_daily()