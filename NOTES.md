TODO: fix clean_dates - dayfirst=True swapped day/month in ISO dates (15,208 rows). Parse both formats explicitly + add date range check.

Docstring on fetch_rates, splitting the long line 39, uv add urllib3, and better commit messages. Ruff and pytest will turn these into a checklist on Day 5.

IMportant that float from pandas can not be same as decimal in db

--SQL reload

for f in sql/03_*.sql sql/04_*.sql sql/05_*.sql sql/06_*.sql sql/08_*.sql; do
    echo "running $f"
    docker exec -i pg psql -U postgres -d payments -v ON_ERROR_STOP=1 < "$f" || break
done




ORA vs GCP:

Database & Analytics Architecture
Oracle Concept                    | GCP Equivalent                            | Key Distinction / Notes
Oracle DB (On-Prem / Exadata)     | AlloyDB for PostgreSQL or Cloud SQL       | AlloyDB is Google's high-performance, enterprise-grade PostgreSQL engine designed to handle heavy transactional/analytical workloads.
Oracle Autonomous Database        | Spanner                                   | Spanner provides horizontal scalability, global consistency, and up to 99.999% availability without sharding.
Oracle Database Sharding          | Cloud Spanner                             | Built natively into the storage architecture; no manual shard management needed.
Oracle PL/SQL                     | Stored Procedures (PostgreSQL / BigQuery) | Rewritten using standard PL/pgSQL (for AlloyDB/Cloud SQL) or BigQuery SQL.
Oracle Data Warehouse (ADW)       | BigQuery                                  | BigQuery is completely serverless and separates compute from storage natively, eliminating database tuning or indexing.

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
BigQuery
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Data type for amount FLOAT after loading to bigquery!

External tables (still a files in Cloud storage) only for rare selection as much slower.
Native tables for regular access (keeps statisticts), much faster.

Need to remember that LIMIT X does not save reading all the table!

In Bq NEVER select * and give particular column names used only!

Checked impersionationg  pdp-loader that load_bigquery.sh execution does the same for another service accounts!



BQ partitioning and clustering:


Partitions and Clusters can be compared to drawers and folders inside them.

If you check particular drawer (partitioned column condition) rest is untouched. Then inside the drawer you quickly check needed folder (condition on clustered column) as folders are ordered.


Reasonable size of partition is important! 

Using partitioned column in query is critical!

When a table is clustered in BigQuery, the table data is automatically organized based on the contents of one or more columns in the table's schema. 
When data is written to a clustered table, BigQuery sorts the data using the values in the clustering columns.

In BigQuery you avoid full scans mainly by selecting only the columns you need, partitioning by date, and clustering by the columns you filter on most; for point lookups on huge tables there are search indexes.


Important to set require_partition_filter = TRUE to avoid unnecessary high resource demanding queries on partitioned tables.


How to check used GBs:

SELECT
  ROUND(SUM(total_bytes_billed) / POW(1024, 3), 2) AS gib_billed_this_month
FROM `region-eu`.INFORMATION_SCHEMA.JOBS
WHERE creation_time >= TIMESTAMP_TRUNC(CURRENT_TIMESTAMP(), MONTH)
  AND job_type = 'QUERY';



Observations when working on reconile procedure:
-----------------------------------------------
1. Compare to PL/SQL BQ functions cannot do DMLs, can be only 'read only'. So procedure as with out parameter have to be used instead;
2. There are differences in compiler, much less details are checked in BQ and more errors can be raised on real execution (still much better than with Postgree procedures).
3. PL/SQL catches specific named exceptions (WHEN NO_DATA_FOUND THEN, WHEN TOO_MANY_ROWS THEN). BQ uses a single catch-all block (EXCEPTION WHEN ERROR THEN) exposing error details through system variables like @@error.message and @@error.statement_text
4. In PL/SQL you can group related procedures, functions, types, and private variables together into Packages. In BQ there is no concept of packages.
5. In PLSQL variables are declared in a dedicated DECLARE section before the BEGIN keyword. In BQ all DECLARE statements has to follow exaclty after BEGIN before any executable statements.


DBT:
-----------------------------------------------------

Snapshots:

Snaphots are powerful and fast set up way to track changes. dbt adds its own dbt_updated_at, dbt_valid_from and dbt_valid_to. Valid record is having dbt_valid_to as NULL.


There are 2 srategy options: timestamp or check. Timestamp option compares a designated timestamp column (updated_at) against the previous snapshot run.
Check option used when there is no 'updated_at' timestamp colum in table.


In check option Only changes configured check_cols are in scope for tracking. Best practice is to use check_cols: All option - this way we track all the changes.


Snapshot is the only model that cannot be rebuild must be treated very carefully not to lost historical data modifications !!!

Snapshots capture state at run time, so intermediate changes are lost and valid_from is the run time. If full history matters, I’d use CDC or a source audit table instead.


Documentation:
-------------------------------------------------------------
To check undocumented parts package dbt_project_evaluator can be used:
  1. Run: uv run dbt build --select +fct_undocumented_models +fct_documentation_coverage
  2. Query the data in BQ: 
      
     -- Models having no documentation
     SELECT *
       FROM `payments-data-platform-pz01126.dbt_dev.fct_undocumented_models`;

     -- coverage of documentation for models
     SELECT *
       FROM `payments-data-platform-pz01126.dbt_dev.fct_documentation_coverage`; 




-------------------------------------------------------------------------------------------------------
Airflow: 
--------------------------------------------------------------------------------------------------------
To install, navigate to orchestration and execute:
navigate to /orchestration

HOST="raw.githubusercontent.com"
FILE="apache/airflow/constraints-3.4.0/constraints-3.12.txt"
uv pip install --python .venv/bin/python "apache-airflow==3.4.0" --constraint "https://${HOST}/${FILE}"




To install apache-airflow-providers-google:

need to modify project.toml  => requires-python = ">=3.12,<3.13" to  resolve dependencies for every future Python version (including 3.15+), where google-cloud-aiplatform fails against the 3.12 constraints file.

THEN
navigate to /orchestration

uv add "apache-airflow==3.4.0" "apache-airflow-providers-google" --constraints https://raw.githubusercontent.com/apache/airflow/constraints-3.4.0/constraints-3.12.txt




* When you trigger a DAG manually, logical_date defaults to the exact current timestamp in UTC at the moment you trigger the run.
* If I set  schedule="@daily", start_date 30 days ago and catchup=True, then unpause the DAG, in such case 30 runs will be scheduled and started, with each run's logical_date set to midnight.
* Using start_date=datetime.now() is a bug because Airflow re-evaluates your DAG file every few seconds, making start_date a constantly moving target in the future that the scheduler can never reach.

.env file example

AIRFLOW_HOME=/home/../orchestration/airflow_home
AIRFLOW__CORE__DAGS_FOLDER=/home/../orchestration/dags
AIRFLOW__CORE__LOAD_EXAMPLES=False




"Retry" approach analyze:
---------------------------------------------------------------------------------------------------------
**upload_files_to_gcs.sh**
- `gcloud storage cp` overwrites objects with the same name, so a retry is OK for fixed file names.
- Risk: the source changes between attempts. `cp` never deletes, so stale files stay in GCS.
  `gcloud storage rsync --delete-unmatched-destination-objects` mirrors the source exactly.
- Better design: a **date parameter** (Airflow passes `{{ ds }}`). Upload only that day's files to
  `gs://…-raw/<table>/dt=YYYY-MM-DD/`. A retry or Clear touches only its own day.
- No date passed means **fail** (no silent default to yesterday: timezone / late-run / backfill risk).
  Use `${1:?usage…}` and validate with `date -d "$1" +%F`.
- Small leftovers: the file count uses `*.parquet` but `cp` copies everything in `domain/`;
  the `cd` in `SOURCE_DIR=$(…)` runs before the `-d` check.

**load_bigquery.sh**
- Idempotent thanks to **`--replace`** (WRITE_TRUNCATE). Without it, `bq load` appends, so every retry
  duplicates the data.
- Load jobs are **atomic**: a failure leaves the table unchanged.
- For daily data, replace the **partition**, not the table: `table$YYYYMMDD --replace`
  (Oracle: `EXCHANGE PARTITION`).


**Recon procedure (recon_run_log / recon_exceptions)**
- Plain INSERTs, so each retry adds rows. That's not wrong: **keeping every run is the audit trail**.
- Store `business_date`, `run_id` (unique per attempt), `started_at`.
- Option A, an `is_last` flag: INSERT + UPDATE, two steps that can become inconsistent and cost extra DML.
- Option B (preferred for logs): **derive** latest in a view:
  `QUALIFY ROW_NUMBER() OVER (PARTITION BY business_date ORDER BY started_at DESC) = 1`,
  then join the exceptions to the latest run_id.
- Rule: append-only logs, derive "current" at read time. Dimensions queried constantly, store it (`is_current`).
- A dbt snapshot doesn't fit: snapshots track **overwritten** rows (merchants), and the log is append-only.
  The reverse design (overwrite a status table + snapshot) loses attempts between snapshot runs.

**dbt incremental (fct_payment_events)**
- MERGE on `unique_key` makes a second run UPDATE matched rows with the same values.
  **Idempotent**, but unnecessary work (part of the ~1.1 GB per run).
- Day 19 bug: `incremental_predicates` filters the **target** side of the MERGE. Target rows outside it are
  invisible, so the source row is NOT MATCHED and gets INSERTed as a duplicate (23,182 duplicates).
- **An incremental MERGE is idempotent only if the target window (predicates) covers at least the
  source window (lookback).**


HOW TO RUN: 

* To start listener process: 

cd ~/dev/payments-data-platform/orchestration
uv run python -c "import sys; print(sys.prefix)"   # expect .../orchestration/.venv
uv run --env-file .env airflow standalone


* To run dag without checking in UI: (dag_id is defined in .py in folder/dags)
   cd ~/dev/payments-data-platform/orchestration
   uv run --env-file .env airflow dags test dag_id


* To stop it press Ctrl+C in CMD or:
ps aux | grep -i airflow | grep -v grep   # see what's still running
pkill -f "airflow"                         # stop all of them