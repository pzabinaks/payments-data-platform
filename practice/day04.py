import os
import time
import pandas as pd
import psycopg
import json

# connection settings: never hard-code passwords in code that goes to GitHub
DSN = os.environ.get("PG_DSN")

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
        t0 = time.perf_counter()  
        
        with cur.copy("COPY payments FROM STDIN") as copy:
            for row in rows:
                #t0 = time.perf_counter() 
                copy.write_row(row)
        
        print(f"execute using copy: {time.perf_counter() - t0:.2f} s")
        conn.commit()

with psycopg.connect(DSN) as conn:
    row_count, paid_total = conn.execute("""
        SELECT COUNT(*),
               SUM(amount) FILTER (WHERE status = 'paid')
        FROM payments
    """).fetchone()
    print(f"rows in DB:      {row_count:,}")
    print(f"paid total (DB): {paid_total:,.2f}")


    df_paid = round(df.loc[df["status"] == "paid", "amount"].sum(), 2)
    print(f"paid total (file): {df_paid:,.2f}")

    assert row_count == len(df), f"row count mismatch: DB {row_count} vs file {len(df)}"
    from decimal import Decimal
    assert paid_total == Decimal(f"{df_paid:.2f}")


with psycopg.connect(DSN) as conn:

    with open(r"data/raw/fx/fx_rates_2026-01-01_2026-10-15.json", 'r') as data_file:
        data = json.load(data_file)

    fx_rows = [(r["date"], r["base"], r["quote"], r["rate"]) for r in data]   # list comprehension, like Day 1

    with conn.cursor() as cursor:
        cursor.executemany("""INSERT INTO fx_rates (rate_date, base, quote, rate)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (rate_date, base, quote) DO UPDATE SET rate = EXCLUDED.rate""", fx_rows)
                    
    fx_count = conn.execute("SELECT COUNT(*) FROM fx_rates").fetchone()[0]
    assert fx_count == len(fx_rows), f"fx rows: DB {fx_count} vs file {len(fx_rows)}"
    
    conn.commit()
    
 
 