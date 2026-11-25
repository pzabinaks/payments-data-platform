from datetime import datetime, timedelta
from pathlib import Path

from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import dag

TRANSFORM_DIR = str(Path(__file__).resolve().parents[2] / "transform")


@dag(
    dag_id="bq_dbt_smoke_test",
    start_date=datetime(2026, 11, 24),
    schedule=None,
    catchup=False,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=1),
    },
    tags=["bigquery", "dbt"],
)
def bq_dbt_smoke_test():
    check_raw_dataset = BashOperator(
        task_id="check_raw_dataset",
        bash_command="bq ls raw",
    )

    run_dbt_debug = BashOperator(
        task_id="run_dbt_debug",
        bash_command="uv run dbt debug",
        cwd=TRANSFORM_DIR,
    )

    print_done = BashOperator(
        task_id="print_done",
        bash_command="echo DONE",
    )

    check_raw_dataset >> run_dbt_debug >> print_done


bq_dbt_smoke_test()