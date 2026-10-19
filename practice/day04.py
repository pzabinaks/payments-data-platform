import os
import time
import pandas as pd
import psycopg

# connection settings: never hard-code passwords in code that goes to GitHub
DSN = os.environ.get("PG_DSN", "postgresql://postgres:devpass@localhost:5432/payments")

df = pd.read_parquet("data/clean/payments.parquet")
rows = list(df.itertuples(index=False, name=None))   # DataFrame -> list of tuples
print(f"rows to load: {len(rows):,}")

with psycopg.connect(DSN) as conn:
    with conn.cursor() as cur:
        cur.execute("TRUNCATE payments")

        # --- Method A: row-by-row INSERT (like conventional path) ---
        t0 = time.perf_counter()
        cur.executemany(
            "INSERT INTO payments VALUES (%s, %s, %s, %s, %s, %s, %s)",
            rows,
        )
        print(f"executemany: {time.perf_counter() - t0:.2f} s")
    conn.commit()

    
with psycopg.connect(DSN) as conn:
    with conn.cursor() as cur:
        cur.execute("TRUNCATE payments")

    with cur.copy("COPY payments FROM STDIN") as copy:
        for row in rows:
            t0 = time.perf_counter() 
            copy.write_row(row)
            print(f"execute using copy: {time.perf_counter() - t0:.2f} s")