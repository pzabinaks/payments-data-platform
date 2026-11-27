from pathlib import Path
import json
import requests
import tempfile

BASE_URL = "https://api.frankfurter.dev/v2/rates"

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


def get_daily_rates(day,quotes,provider):
    session = make_session()
    rates = fetch_rates(session,day, day, quotes, provider)
    file_path = Path(tempfile.gettempdir()) / f"fx_rates_{day}.json"
    file_path.write_text(json.dumps(rates, indent=2), encoding="utf-8")
    
    return str(file_path)