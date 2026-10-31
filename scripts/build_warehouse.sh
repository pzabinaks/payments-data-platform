#!/usr/bin/env bash
set -euo pipefail

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

DB_USER="${POSTGRES_USER:-postgres}"
DB_NAME="${POSTGRES_DB:-postgres}"

# Define the array of SQL script names in execution order
SQL_SCRIPTS=(
    "03_dim_date.sql"
    "04_dimensions.sql"
    "05_fct_payments.sql"
    "06_fct_payment_transactions.sql"   
    "09_dim_merchant_scd2.sql" 
    "08_merchant_changes.sql"
    "10_p_apply_merchant_batch.sql"
    "11_apply_merchant_batch.sql"
)
SCRIPT_DIR="sql"

# 1 ---- Create payments and fx_rate tables
docker compose exec -T pgdatabase psql -v ON_ERROR_STOP=1 -U "$DB_USER" -d "$DB_NAME" < "sql/01_create_tables.sql"

# 2 -------  Python scripts --------------------------------------------------------------------------
uv run python -m payments_data_platform.load_staging;  # create/load  staging tables
uv run python -m practice/day08_fx.py;  #  fix rates

# 3 -------  SQL part --------------------------------------------------------------------------
# Loop through each script in the array and execute it
    # "03_dim_date.sql"                        --- create date dimention table
    # "04_dimensions.sql"                      -- rest of the dimention tables
    # "05_fct_payments.sql"                    -- creaete payment fact tables
    # "06_fct_payment_transactions.sql"        -- payment transaction fact table
    # "09_dim_merchant_scd2.sql"               -- create scd for dim_merchant
    # "08_merchant_changes.sql"                -- create merchant stg change tables
    # "10_p_apply_merchant_batch.sql"          -- create procedure to hanlde merchant scd
    # "11_apply_merchant_batch.sql"            -- apply merchant changes and handle scd


for script in "${SQL_SCRIPTS[@]}"; do
    # Combine the directory and file name into a full path
    full_path="${SCRIPT_DIR}/${script}"

    if [ -f "$full_path" ]; then
        echo "Executing: $full_path..."
        
        # Stream the file from the local 'sql/' directory into the container
        docker compose exec -T pgdatabase psql -v ON_ERROR_STOP=1 -U "$DB_USER" -d "$DB_NAME" < "$full_path"
        
    else
        echo "Error: File '$full_path' not found. Aborting."
        exit 1
    fi
done

echo "All scripts from the '$SCRIPT_DIR' folder executed successfully."
