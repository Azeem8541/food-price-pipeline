import os
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests
import boto3
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=ROOT / ".env")
API_KEY = os.getenv("DATA_GOV_API_KEY")
if not API_KEY:
    raise SystemExit("API key nahi mili. .env check karo.")

RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"
URL = f"https://api.data.gov.in/resource/{RESOURCE_ID}"
PAGE_SIZE = 500
MAX_TRIES = 5
RAW_DIR = ROOT / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# Gateway default python-requests User-Agent ko hang/reject karta hai,
# isliye browser jaise headers bhej rahe hain.
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"),
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_page(session, offset):
    params = {"api-key": API_KEY, "format": "json",
              "limit": PAGE_SIZE, "offset": offset}
    for attempt in range(1, MAX_TRIES + 1):
        try:
            resp = session.get(URL, params=params, timeout=(10, 90))
            if resp.status_code == 200:
                return resp.json()
            print(f"  offset={offset} status={resp.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"  offset={offset} attempt={attempt} {type(e).__name__}")
        time.sleep(5 * attempt)
    raise RuntimeError(f"offset={offset} par {MAX_TRIES} tries ke baad bhi fail")


def main():
    run_ts = datetime.now(timezone.utc)
    session = requests.Session()
    session.headers.update(HEADERS)
    records, offset, total = [], 0, None

    while True:
        data = fetch_page(session, offset)
        if total is None:
            total = int(data.get("total", 0))
            print("API total records:", total)
        batch = data.get("records", [])
        if not batch:
            break
        for i, r in enumerate(batch):
            r["_page_offset"] = offset
            r["_row_in_page"] = i
        records.extend(batch)
        offset += len(batch)
        print(f"Fetched {offset}/{total}")
        if offset >= total:
            break
        time.sleep(1)  # server pe halka load

    if not records:
        raise SystemExit("Koi record nahi aaya.")

    df = pd.DataFrame(records).astype(str)  # raw layer: jaisa aaya waisa hi
    df["_ingested_at"] = run_ts.isoformat()
    df["_source"] = "data.gov.in/agmarknet"

    out = RAW_DIR / f"mandi_{run_ts:%Y-%m-%d_%H%M%S}.parquet"
    df.to_parquet(out, index=False)
    print(f"Saved {len(df)} rows -> {out}")
    bucket = os.getenv("S3_BUCKET")
    if bucket:
        s3_key = f"bronze/mandi/ingest_date={run_ts:%Y-%m-%d}/{out.name}"
        boto3.client("s3").upload_file(str(out), bucket, s3_key)
        print(f"Uploaded -> s3://{bucket}/{s3_key}")
    else:
        print("S3_BUCKET set nahi hai, upload skip.")
    print("Distinct states:", df["state"].nunique(),
          "| markets:", df["market"].nunique(),
          "| commodities:", df["commodity"].nunique())


if __name__ == "__main__":
    main()