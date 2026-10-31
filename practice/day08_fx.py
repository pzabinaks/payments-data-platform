import psycopg
import json
import os
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter  # part of requests
from urllib3.util.retry import Retry  # urllib3 is installed automatically together with request


# Fetch ratas and save in json

BASE_URL = "https://api.frankfurter.dev/v2/rates"
START, END = "2024-12-15", "2026-10-15"
FILENAME = f"fx_rates_{START}_{END}.json"


def fetch_rates_old(start, end, quotes, providers):
    """Fetch daily EUR exchange rates between start and end (YYYY-MM-DD)."""
    r = requests.get(
        BASE_URL,
        params={"from": start, "to": end, "quotes": quotes, "providers": providers},
        timeout=10,
    )
    r.raise_for_status()  # stop with an error on 4xx/5xx
    return r.json()


def save_raw(data, start, end):
    savepath = Path("data/raw/fx")
    savepath.mkdir(parents=True, exist_ok=True)
    filename = savepath / FILENAME

    # create file
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def make_session():
    retry = Retry(
        total=3,  # at most 3 retries
        backoff_factor=1,  # wait about 1s, 2s, 4s between them
        status_forcelist=[429, 500, 502, 503, 504],  # only retry these status codes
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))  # apply to all https:// calls
    return session


def fetch_rates(session, start, end, quotes, providers):
    r = session.get(
        BASE_URL,
        params={"from": start, "to": end, "quotes": quotes, "providers": providers},
        timeout=10,
    )  # session.get instead of requests.get
    r.raise_for_status()
    return r.json()


session = make_session()
rates = fetch_rates(session, START, END, "gbp,usd", "ecb")
save_raw(rates, START, END)


# connection settings: never hard-code passwords in code that goes to GitHub
DSN = os.environ.get("PG_DSN")

f"fx_rates_{START}_{END}.json"
with psycopg.connect(DSN) as conn:
    with open(f"data/raw/fx/{FILENAME}", "r") as data_file:
        data = json.load(data_file)

    fx_rows = [
        (r["date"], r["base"], r["quote"], r["rate"]) for r in data
    ]  # list comprehension, like Day 1

    with conn.cursor() as cursor:
        cursor.executemany(
            """INSERT INTO fx_rates (rate_date, base, quote, rate)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (rate_date, base, quote) DO UPDATE SET rate = EXCLUDED.rate""",
            fx_rows,
        )

    fx_count = conn.execute("SELECT COUNT(*) FROM fx_rates").fetchone()[0]
    assert fx_count == len(fx_rows), f"fx rows: DB {fx_count} vs file {len(fx_rows)}"

    conn.commit()
