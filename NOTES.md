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


BigQuery

Data type for amount FLOAT after loading to bigquery!

External tables (still a files in Cloud storage) only for rare selection as much slower.
Native tables for regular access (keeps statisticts), much faster.

Need to remember that LIMIT X does not save reading all the table!

In Bq NEVER select * and give particular column names used only!

Checked impersionationg  pdp-loader that load_bigquery.sh execution does the same for another service accounts!



BQ partitioning and clustering:



Reasonable size of partition is important! 

Using partitioned column in query is critical!


Partition similar to Oracle, Clustering is the instrumentation for performance like oracle create index.


Important to set require_partition_filter = TRUE to avoid unnecessary high resource demanding queries on partitioned tables.