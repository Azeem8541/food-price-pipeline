import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")
API_KEY = os.getenv("DATA_GOV_API_KEY")
if not API_KEY:
    raise SystemExit("API key nahi mili. .env check karo.")

RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"
URL = f"https://api.data.gov.in/resource/{RESOURCE_ID}"

params = {
    "api-key": API_KEY,
    "format": "json",
    "limit": 5,
    "offset": 0,
}

MAX_TRIES = 4
for attempt in range(1, MAX_TRIES + 1):
    try:
        print(f"Attempt {attempt}/{MAX_TRIES} ...")
        # (connect timeout, read timeout)
        resp = requests.get(URL, params=params, timeout=(10, 90))
        print("Status:", resp.status_code)
        if resp.status_code == 200:
            break
        print(resp.text[:300])
    except requests.exceptions.RequestException as e:
        print("Failed:", type(e).__name__)
    time.sleep(5 * attempt)  # 5s, 10s, 15s wait
else:
    raise SystemExit("Saari attempts fail. Browser test karo ya baad mein try karo.")

data = resp.json()
print("Total records available:", data.get("total"))
print("Fields:", [f["id"] for f in data.get("field", [])])
for rec in data.get("records", [])[:3]:
    print(rec)