Welcome to your new dbt project!

### What it is:

Dbt project that trasforms raw  direct-debit style payment data ib BigQuery into a tested star schema.




### Layers:

| Layer | Details | BQ dataset 
|---|---|---
| **sources(raw)** | Raw data expected to be loaded to dataset 'raw'. Following raw tables used as sources:|
|              | **customers**  - Customer data for payments | raw
|              | **merchants**  - Merchants involved for payments  | raw                                                                                
|              | **mandates**   - Defined mandates to link customer with merchant| raw
|              | **payments**   - Payment information| raw
|              | **events**     - Table holding payment events data. All the history for payment with statuses| raw
| **staging**  | Layer build on sources with some minor transformations - timestampt to date, float to number|
|              | **stg_customers**  - Customer data for payments| staging
|              | **stg_merchants**  - Merchants involved for payments   | staging                                                                               
|              | **stg_mandates**   - Defined mandates to link customer with merchant| staging
|              | **stg_payments**   - Payment information (amount transformed from float to number.charge_date to date from timestamp )| staging
|              | **stg_events**     - Table holding payment events data. All the history for payment with statuses| staging
| **intermediate**  | For now payment milestone transformation for later usage in marts|
|              | **int_payement_milestones**  - Intermediate payment table - with all statuse dates in one line| intermediate
| **marts**  | Layer for fact tables and dimentions|
|              | **dim_customer**  - Customer dimention table| marts
|              | **dim_dates**     - Dates dimention table| marts
|              | **dim_mandates**  - Mandates dimention table| marts
|              | **dim_merchants** - Merchants dimention table| marts
|              | **fct_payments** - Main payment fact table| marts
|              | **fct_payment_events** - Payement event fact table| marts
|---|---|---
| **seeds**  | Layer for seeds|
|            | **counries.csv** - Country codes and names. Used in fact tables and validations|
| **snapshots**  | Layer for snapshots|
|            | **merchant_snapshot** - Country codes and names. Used in fact tables and validations|snapshots



### Materialization:

| Layer | Materialization| Comments
|---|---|---
| **staging**  | View |
| **intermediate**  | View |
| **marts**  | Table |
| **fct_payment_events**  | Incremental | Incremental approuch used here. Merge based on event_at timestamp



### Setup:

    Prerequisites:

    * **Python & `uv`:** Install [uv](https://astral.sh).
    * **Google Cloud CLI:** Install the [Google Cloud SDK (`gcloud`)](https://google.com).



1. Execute command: 

    ```bash
    uv sync
    ```

   Why: To sync/update your project's virtual environment



2. **Configure pacgages.yml adding dbt_utils and dbt_project_evaluator packages used in this project**
   Example:

    ```yaml
      packages:
      - package: dbt-labs/dbt_utils
        version: 1.4.1

      - package: dbt-labs/dbt_project_evaluator
        version: [">=0.14.0", "<2.0.0"]  
    ```

   Execute command:

    ```bash
    uv run dbt deps
    ```

   Why: To install the configured packages. dbt_utils used for validations and dbt_project_evaluator used for project best practices analyze


3. **Authenticate with Google Cloud**

   Log in to generate Application Default Credentials (ADC) so dbt can connect to BigQuery via OAuth:

   ```bash
   gcloud auth application-default login
   ```


4. **Set up  .dbt/profiles.yml**
   Example:
   
   ```yaml
     project_name:
       target: dev # this sets dev as default profile
       outputs:
         dev:
           dataset: dbt_dev                         # default dataset name for dev profile
           job_execution_timeout_seconds: 300       # Timeout for job execution
           job_retries: 1                           # Retries
           location: EU                             # Location zone 
           method: oauth                            # Authorization mode
           priority: interactive
           project: your_project_id                 # BQ project id  
           threads: 4                               # Threads used
           type: bigquery
           maximum_bytes_billed: 1000000000         # Limit for controlling usage of bytes for job

         prod:
           dataset: analytics
           job_execution_timeout_seconds: 300
           job_retries: 1
           location: EU
           method: oauth
           priority: interactive
           project: your_project_id
           threads: 4
           type: bigquery
           maximum_bytes_billed: 2000000000   # 1 GB per query  
    ```
    *(Replace `project_name` and `your_project_id` with your dbt project name and GCP project ID.)*

5. **Verify the connection**

   Test that dbt can read your profile and authenticate with BigQuery:

   ```bash
   uv run dbt debug
   ```

### Running it:

* **`uv run dbt build`** — Runs models, executes tests, loads seeds, and updates snapshots in DAG order against your default `dev` target (`dbt_dev` dataset).
* **`uv run dbt build --target prod`** — Runs the full build pipeline (models, tests, seeds, snapshots) against your `prod` target (`analytics` dataset).
* **`uv run dbt snapshot`** — Captures historical changes in mutable source tables over time (Type 2 Slowly Changing Dimensions) using valid-from and valid-to timestamps.
* **`uv run dbt source freshness`** — Checks raw source table timestamps against configured SLA thresholds to verify upstream data is up to date.
* **`uv run dbt docs generate`** — Compiles your project's metadata, catalog, and lineage graph into static documentation files.
* **`uv run dbt docs serve`** — Launches a local web server to view the generated interactive documentation in your browser.
* **`uv run dbt parse --show-all-deprecations`** - Validates your dbt project's YAML, Jinja, and SQL syntax without executing any queries against BigQuery, and prints every single deprecation warning in your project instead of stopping at the first occurrence.
* **`uv run dbt build --full-refresh`** - To force all incremental models to perform a full reload during 


### Testing: 

| Coverage | Severity | Details 
|---|---|---
| **keys**  |Error| All keys of mart created fct_ and dim_ tables  have -unique and -not_null data_tests defined
| **relationships**  |Error| fct_payments - all charge_date_sk/submitted_date_sk/confirmed_date_sk/paid_out_date_sk/charged_back_date_sk/pending_submission_date_sk is checked for value of dim_date.date_sk
|                    |Error| stg_events - payment_id exists in stg_paments.payment_id
|                    |Error| stg_mandates - customer_id exists in stg_customer.customer_id
|                    |Error| stg_mandates - merchant_id exists in stg_merchants.merchant_id
|                    |Error| stg_merchants - country exists in countries.csv seed
|                    |Error| stg_payments  - mandate_id exists in stg_mandates.mandate_id
| **accepted values** |Error| stg_payments  - status in: 'paid_out','failed','confirmed','charged_back','submitted'
|                     |Error| stg_payments  - currency in: 'EUR','GBP'
|                     |Error| stg_event  - status in: 'charged_back','confirmed','failed','paid_out','pending_submission','submitted'
|**reconciliation tests** |Error| fct_payment_events_reconciliation_check.sql - Verifies that rerord counts in fct_payment_events and stg_events is the same
|**dbt_utils tests** |Error| fct_payments.days_to_payout - dbt_utils.expression_is_true:  ">= 0" used here. In case of false the record will be stored in validation table (store_failures: true )
|                    |Warning| fct_payments.days_to_charge_back - dbt_utils.accepted_range: min_value: 10  max_value: 60

**Test coverage:**

Using dbt_project_evaluator:
 ```bash
   uv run dbt build --select package:dbt_project_evaluator
   ```
We can check tables to get testing coverage related information:
 * **fct_missing_primary_key_tests**   - Flags models that do not have both unique and not_null tests
 * **fct_sources_without_freshness**   - Identifies declared sources that lack warn_after or error_after freshness checks
 * **fct_test_coverage**              - Overall Coverage/Test-to-Model Ratio/ Coverage by Model Type


### Some design decisions:

* **Monthly partitions**  - Decision was made to parition table fct_payements by charge_date with granularity month. As analyzing data it was clear that avarage payment count for one month is about 82k, and as most probably accessing fact table in most time is filtered by payment date in some interval.

* **Hash surrogate keys instead of sequences** - Decision was made to use hash keys (dbt_utils.generate_surrogate_key(natural_key)) because hashing natural keys ensures keys are deterministic, idempotent across incremental runs, and safe for parallel processing.


* **The 1 GB / 2 GB cost caps** - As we have incremental materialization for fct_payment_events and source 'events' are big table here ( 3.8 mil records) each run have to analyze all the records according by event_at column. That is the reason for prod mode in profiles.yml is doubled compare to dev mode. In dev mode we can use uv run dbt build --full-refresh.

* **The evaluator disabled in prod** - dbt_project_evaluator inspects your DAG, naming conventions, documentation, and test coverage—metadata that only changes when code is modified, not when new production data arrives. So running it in prod wastes compute, clutters schemas, and risks unnecessary alerts without adding runtime value.


* **Snapshot with check_cols: all** - Setting up a dbt snapshot with check_cols: all  here makes sense becaus that way we automatically captures historical changes across every column in a table without requiring a reliable updated_at timestamp or manual column maintenance.