"""Load the generated domain Parquet files into PostgreSQL staging tables (ELT: load raw, transform in SQL)."""

import io
import logging
import os
from pathlib import Path

import pandas as pd
import psycopg

logger = logging.getLogger(__name__)

DSN = os.environ.get("PG_DSN")
DOMAIN_DIR = Path("data/raw/domain")


def pg_type(dtype) -> str:
    """Map a pandas column type to a PostgreSQL type."""
    if dtype.kind in "iu":  # integers
        return "bigint"
    if dtype.kind == "f":  # floats -> exact numeric (money!)
        return "numeric"
    if dtype.kind == "b":
        return "boolean"
    if dtype.kind == "M":  # datetime
        return "timestamp"
    return "text"


def load_table(conn: psycopg.Connection, name: str, df: pd.DataFrame) -> None:
    """Recreate stg_<name> with matching columns and bulk-load df into it with COPY."""
    table = f"stg_{name}"
    columns = ", ".join(f"{col} {pg_type(df[col].dtype)}" for col in df.columns)

    with conn.cursor() as cur:
        cur.execute(f"DROP TABLE IF EXISTS {table}")
        cur.execute(f"CREATE TABLE {table} ({columns})")

        buffer = io.StringIO()  # the DataFrame as CSV text, in memory
        df.to_csv(buffer, index=False, header=False)
        buffer.seek(0)
        with cur.copy(f"COPY {table} FROM STDIN WITH (FORMAT csv)") as copy:
            copy.write(buffer.read())

        db_rows = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    if db_rows != len(df):
        raise ValueError(f"{table}: file has {len(df)} rows, database has {db_rows}")
    logger.info("%-22s %10s rows", table, f"{db_rows:,}")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-7s %(message)s")
    with psycopg.connect(DSN) as conn:
        for path in sorted(DOMAIN_DIR.glob("*.parquet")):
            load_table(conn, path.stem, pd.read_parquet(path))
        conn.commit()


if __name__ == "__main__":
    main()
