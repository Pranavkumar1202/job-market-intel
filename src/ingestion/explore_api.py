import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

URL = "https://api.adzuna.com/v1/api/jobs/in/search/1"

params = {
    "app_id": os.environ["ADZUNA_APP_ID"],
    "app_key": os.environ["ADZUNA_APP_KEY"],
    "results_per_page": 10,
    "what": "data analyst",
    "content-type": "application/json",
}

resp = requests.get(URL, params=params, timeout=30)
resp.raise_for_status()
data = resp.json()

os.makedirs("data", exist_ok=True)
with open("data/sample_response.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("Total matches:", data.get("count"))
for job in data["results"][:5]:
    print("-", job.get("title"), "|", job.get("company", {}).get("display_name"),
          "|", job.get("location", {}).get("display_name"),
          "|", job.get("salary_min"), "-", job.get("salary_max"))