from pathlib import Path
import json
import requests
import pandas as pd
from requests.adapters import HTTPAdapter     # part of requests
from urllib3.util.retry import Retry          # urllib3 is installed automatically together with request


BASE_URL = "https://api.frankfurter.dev/v2/rates"

def fetch_rates_old(start, end, quotes,providers):
    """Fetch daily EUR exchange rates between start and end (YYYY-MM-DD)."""
    r = requests.get(BASE_URL,
                     params={"from": start, "to": end, "quotes": quotes,"providers": providers},
                     timeout=10)
    r.raise_for_status()          # stop with an error on 4xx/5xx
    return r.json()

def save_raw(data, start, end):
    savepath = Path("data/raw/fx")
    savepath.mkdir(parents=True, exist_ok=True)
    filename = savepath / f"fx_rates_{start}_{end}.json"

    #create file
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def make_session():
    retry = Retry(
        total=3,                                  # at most 3 retries
        backoff_factor=1,                         # wait about 1s, 2s, 4s between them
        status_forcelist=[429, 500, 502, 503, 504],  # only retry these status codes
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))   # apply to all https:// calls
    return session

def fetch_rates(session, start, end, quotes, providers):
    r = session.get(BASE_URL, params={"from": start, "to": end, "quotes": quotes,"providers": providers}, timeout=10)    # session.get instead of requests.get
    r.raise_for_status()
    return r.json()

session = make_session()
rates = fetch_rates(session,"2026-01-01", "2026-10-15", "gbp,usd", "ecb")
save_raw(rates, "2026-01-01", "2026-10-15")

df = pd.DataFrame(rates)
df["date"] = pd.to_datetime(df["date"])


assert not df["date"].dt.day_name().isin(["Sunday", "Saturday"]).any(), "Weekend dates!"

dupes = df.duplicated(subset=["date", "base", "quote"], keep=False).sum()
assert dupes == 0, f"{dupes} duplicate rate rows!"

print("rates per currency:")
print(df.groupby("quote")["rate"].agg(["count", "min", "max"]))

# --- failure tests ---
tests = {
    "wrong path":       ("https://api.frankfurter.dev/v2/ratez", {"quotes": "gbp"}),
    "invalid currency": (BASE_URL, {"quotes": "EUR", "providers": "ecb"}),
    "weekend date":         (BASE_URL, {"from": "2026-10-03","to": "2026-10-04","quotes": "gbp", "providers": "ecb"}),
}

for name, (url, params) in tests.items():
    try:
        r = session.get(url, params=params, timeout=10)
        
        if not rates:
            raise ValueError("API returned no rates for this period")
        
        print(f"{name:18} status {r.status_code}")
        r.raise_for_status()
        print(f"{name:18} no error raised! response: {r.text[:100]}")
    except requests.exceptions.HTTPError as e:
        print(f"{name:18} HTTPError: {e}")