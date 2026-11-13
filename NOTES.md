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


Observations when working on reconile procedure:
-----------------------------------------------
1. Compare to PL/SQL BQ functions cannot do DMLs, can be only 'read only'. So procedure as with out parameter have to be used instead;
2. There are differences in compiler, much less details are checked in BQ and more errors can be raised on real execution (still much better than with Postgree procedures).
3. PL/SQL catches specific named exceptions (WHEN NO_DATA_FOUND THEN, WHEN TOO_MANY_ROWS THEN). BQ uses a single catch-all block (EXCEPTION WHEN ERROR THEN) exposing error details through system variables like @@error.message and @@error.statement_text
4. In PL/SQL you can group related procedures, functions, types, and private variables together into Packages. In BQ there is no concept of packages.
5. In PLSQL variables are declared in a dedicated DECLARE section before the BEGIN keyword. In BQ all DECLARE statements has to follow exaclty after BEGIN before any executable statements.