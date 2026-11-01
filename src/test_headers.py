import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")
API_KEY = os.getenv("DATA_GOV_API_KEY")

URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
params = {"api-key": API_KEY, "format": "json", "limit": 5, "offset": 0}

headers = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"),
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "en-US,en;q=0.9",
}

for name, h in [("default python UA", None), ("browser UA", headers)]:
    try:
        r = requests.get(URL, params=params, headers=h, timeout=(10, 60))
        print(f"{name}: status={r.status_code}, bytes={len(r.content)}")
    except requests.exceptions.RequestException as e:
        print(f"{name}: {type(e).__name__}")