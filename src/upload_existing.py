import os
import re
from pathlib import Path

import boto3
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=ROOT / ".env")
bucket = os.getenv("S3_BUCKET")
if not bucket:
    raise SystemExit("S3_BUCKET nahi mila.")

s3 = boto3.client("s3")
for f in sorted((ROOT / "data" / "raw").glob("mandi_*.parquet")):
    m = re.search(r"mandi_(\d{4}-\d{2}-\d{2})_", f.name)
    if not m:
        continue
    key = f"bronze/mandi/ingest_date={m.group(1)}/{f.name}"
    try:
        s3.head_object(Bucket=bucket, Key=key)
        print("Already there:", key)
    except Exception:
        s3.upload_file(str(f), bucket, key)
        print("Uploaded:", key)