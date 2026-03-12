import requests
import time
from secrects import SEMANTIC_SCHOLAR_API_KEY

def fetch_papers(topic, limit, retries=1, wait_seconds=5):
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    headers = {
        "x-api-key": SEMANTIC_SCHOLAR_API_KEY
    }

    params = {
        "query": topic,
        "limit": limit,
        "fields": "title,authors,year,abstract,url,openAccessPdf"
    }

    for attempt in range(retries):
        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            return response.json()["data"]

        elif response.status_code == 429:
            print(f"Rate limit hit. Waiting {wait_seconds} seconds...")
            time.sleep(wait_seconds)

        else:
            response.raise_for_status()

    print("Could not fetch papers due to repeated rate limiting.")
    return []