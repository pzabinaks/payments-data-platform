import os
import time
import pandas as pd
import psycopg
import json

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


with psycopg.connect(DSN) as conn:

    with open(r"/home/pzabinaks/dev/payments-data-platform/data/raw/fx/fx_rates_2026-01-01_2026-10-15.json", 'r') as data_file:
        data = json.load(data_file)

    for item in data:
    # Replace the keys below with the keys in your JSON data
        date = item['date']
        base = item['base']
        quote = item['quote']
        rate = item['rate']

    with conn.cursor() as cursor:
        cursor.execute("""INSERT INTO fx_rates (rate_date, base, quote, rate)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (rate_date, base, quote) DO UPDATE SET rate = EXCLUDED.rate""", (date, base, quote, rate))
                    
    conn.commit()
    conn.close()