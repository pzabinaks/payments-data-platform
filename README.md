# Payments Data Platform

A small, end-to-end data platform for **direct-debit style payment data**, built step by step
with a focus on **data quality, reconciliation and reproducibility**.

It takes a messy legacy-style payments export, cleans and validates it, enriches it with official
**ECB exchange rates** from a REST API, loads everything into **PostgreSQL**, and converts GBP
payments to EUR with an as-of join, with every step checked against the source.

> Work in progress: this repository follows an 8-week learning plan from SQL/Oracle data migration
> work towards a modern data engineering stack (BigQuery, dbt, Airflow). See [Roadmap](#roadmap).

---

## What it does today

| Step | What | Where |
|---|---|---|
| 1. Profile & clean | Finds and fixes 9 data quality issues in a 50,600-row raw export; one tested function per rule | `src/payments_data_platform/cleaning.py` |
| 2. Reconcile | Row counts, totals, date-range and duplicate checks act as quality gates before anything is written | `practice/day02.py` (to be moved into the package) |
| 3. Store | Writes clean data as Parquet (typed, columnar) alongside CSV and JSON for comparison | `data/clean/` (not in Git) |
| 4. Extract FX rates | Calls the Frankfurter API (ECB provider) with retries and data-contract checks | `practice/day03.py` |
| 5. Load | PostgreSQL in Docker with keys and CHECK constraints; bulk `COPY` load; idempotent upsert for rates | `sql/01_create_tables.sql`, `practice/day04.py` |
| 6. Convert currency | As-of join (latest ECB rate on or before the payment date), in both SQL and pandas, reconciled to the cent | `sql/02_gbp_to_eur.sql`, `practice/day06.py` |

## Key results

- **9 data quality issues** found by profiling the raw export (see below), each fixed by a small,
  tested function.
- **A silent date bug caught and locked down:** automatic date parsing swapped day and month for
  15,208 records. Profiling exposed it (payments dated in the future), and a date-range gate plus a
  regression test now prevent it.
- **Reconciled end to end:** 50,600 rows read → 600 exact duplicates removed → 50,000 rows written;
  paid total **4,020,886.99** matches in pandas and in PostgreSQL.
- **Bulk loading:** `COPY` loaded 50,000 rows **5.5× faster** than batched `INSERT`s (0.16 s vs 0.88 s,
  local database).
- **Currency conversion:** 4,864 GBP payments, all matched to an ECB rate (0 missing). The EUR total
  is identical in SQL and pandas once both round per transaction.

## Data quality issues found in the raw export

| # | Issue | Example | Rule |
|---|---|---|---|
| 1 | Column names with spaces / mixed case | `' Customer '`, `Created At` | snake_case, rename to `customer_id` |
| 2 | Status in mixed case | `PAID`, `Paid`, `paid` | lowercase |
| 3 | Trailing spaces in status | `'paid '` | strip |
| 4 | Currency in mixed case | `eur` | uppercase (ISO 4217) |
| 5 | Leading spaces in currency | `' EUR'` | strip |
| 6 | Decimal comma in amounts | `75,50` | convert to `75.50` |
| 7 | Two date formats in one column | `2026-08-01 16:19:49` and `07.09.2026` | parse each format explicitly; the second has no time of day |
| 8 | Missing customer IDs | 482 rows | keep the payment, mark the customer as `UNKNOWN` |
| 9 | Exact duplicate rows | 600 rows | remove, keep the first occurrence |

## Design decisions

- **Explicit date formats, never guessing.** `format="mixed"` with `dayfirst=True` silently swapped
  day and month in ISO dates. Each format is now parsed explicitly and the results combined.
- **Official ECB rates only.** The API blends ~100 sources by default (including weekend rates);
  financial reporting needs the official reference rate, so requests use `providers=ecb`.
- **Data contracts on API responses.** No weekend dates, no duplicates per `(date, base, quote)`, and
  every returned date must fall inside the requested range. The API returns the previous business
  day when a range has no data, so this check matters.
- **Lookback window for rates.** The as-of join needs a rate *before* the first payment (1 January is
  an ECB holiday), so rates are fetched from before the reporting period starts.
- **Money is exact.** Amounts are `numeric(12,2)` in PostgreSQL, never `float`. Reconciliation compares
  as `Decimal` to the cent, and conversions are rounded per transaction, then summed (accounting
  convention).
- **Idempotent loads.** Re-running the rate load updates existing rows (`ON CONFLICT ... DO UPDATE`)
  instead of failing or duplicating them.

## Project structure

```
payments-data-platform/
├── src/payments_data_platform/
│   ├── __init__.py        # pipeline entry point: read raw CSV -> clean -> write Parquet (with logging)
│   └── cleaning.py        # one function per cleaning rule + clean_payments() pipeline
├── tests/
│   └── test_cleaning.py   # unit tests per rule, end-to-end test, date regression tests
├── sql/
│   ├── 01_create_tables.sql   # payments + fx_rates with keys and CHECK constraints
│   └── 02_gbp_to_eur.sql      # as-of join (LEFT JOIN LATERAL) GBP -> EUR
├── practice/              # day-by-day exploration scripts (profiling, API, loading, SQL -> pandas)
├── pyproject.toml         # dependencies, ruff and pytest configuration
└── uv.lock                # exact, reproducible dependency versions
```

## How to run

**Prerequisites:** Linux or WSL2, [uv](https://docs.astral.sh/uv/), Docker.

```bash
# install Python 3.12 and all dependencies exactly as locked
uv sync

# run the tests and the linter
uv run pytest -v
uv run ruff check src tests

# run the cleaning pipeline (expects the raw export in data/raw/payments_raw.csv)
uv run payments-data-platform

# start PostgreSQL and create the tables
cp .env.example .env        # then set your own passwords
   docker compose up -d --wait
   ./scripts/build_warehouse.sh

# fetch ECB rates, then load payments and rates into PostgreSQL
uv run python practice/day03.py
uv run python practice/day04.py

# convert GBP payments to EUR
docker exec -i pg psql -U postgres -d payments < sql/02_gbp_to_eur.sql
```

The input file is a **synthetic** payments export with realistic legacy-system problems; it contains
no real customer data. Data files are not committed to Git (`data/` is ignored); code creates or
downloads them.

## Tech stack

Python 3.12 · pandas · PyArrow / Parquet · requests · psycopg 3 · PostgreSQL 17 · Docker ·
pytest · ruff · uv · Git

## Roadmap

- [x] Python foundations: files, APIs, PostgreSQL, tests, linting, logging
- [x] SQL → pandas translations (aggregates, window functions, as-of joins)
- [x] Payments domain generator (mandates, failures, retries, late-arriving updates)
- [x] Dimensional model: star schema, slowly changing dimensions (SCD2)
- [ ] Google Cloud: Cloud Storage, BigQuery (partitioning, clustering), Terraform
- [ ] dbt: staging and mart models with tests and documentation
- [ ] Airflow: scheduled, idempotent pipeline with backfills
- [ ] CI with GitHub Actions; data governance (PII masking)
- [ ] ML/AI on top: payment-failure prediction (BigQuery ML), LLM-based classification

## Author

**Peteris Zabinaks**: 15+ years of data migration, data quality and database engineering
(Oracle, PostgreSQL) in financial services and telecom, now working on modern data engineering.
