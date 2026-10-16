from pathlib import Path
import json
import requests

BASE_URL = "https://api.frankfurter.dev/v2/rates"

def fetch_rates(start, end, quotes,providers):
    """Fetch daily EUR exchange rates between start and end (YYYY-MM-DD)."""
    r = requests.get(BASE_URL,
                     params={"from": start, "to": end, "quotes": quotes,"providers": providers},
                     timeout=10)
    r.raise_for_status()          # stop with an error on 4xx/5xx
    return r.json()

def save_raw(data, start, end):
    savepath = Path("data/raw/fx")
    savepath.mkdir(parents=True, exist_ok=True)
    filename  = "data/raw/fxfx_rates_" +start+ "_"+end+".json"

    #create file
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

    ...   # your task: write data as JSON to data/raw/fx/fx_rates_<start>_<end>.json
          # hints: Path(...).mkdir(parents=True, exist_ok=True), json.dump(data, f, indent=2)


rates = fetch_rates("2026-01-01", "2026-10-15", "gbp,usd",'ecb')
#print(rates)
print(f"records fetched: {len(rates)}")
save_raw(rates, "2026-01-01", "2026-10-15")