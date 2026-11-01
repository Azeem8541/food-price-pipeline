import os
from pathlib import Path

import boto3
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")
bucket = os.getenv("S3_BUCKET")
if not bucket:
    raise SystemExit("S3_BUCKET .env mein nahi mila.")

s3 = boto3.client("s3")  # keys env se khud padh leta hai

s3.put_object(Bucket=bucket, Key="test/hello.txt", Body=b"hello from laptop")
print("Upload OK")

obj = s3.get_object(Bucket=bucket, Key="test/hello.txt")
print("Read back:", obj["Body"].read().decode())

s3.delete_object(Bucket=bucket, Key="test/hello.txt")
print("Delete OK")