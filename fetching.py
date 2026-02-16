import requests
import time
import os
from secrects import SEMANTIC_SCHOLAR_API_KEY
def fetch_papers(topic, limit, retries=1, wait_seconds=5):
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    headers={
        "x-api-key" : SEMANTIC_SCHOLAR_API_KEY
    }

    params = {
        "query": topic,
        "limit": limit,
        "fields": "title,authors,year,abstract,url,openAccessPdf"
    }

    for attempt in range(retries):
        response = requests.get(url, params=params,headers=headers)

        if response.status_code == 200:
            return response.json()["data"]

        elif response.status_code == 429:
            print(f"Rate limit hit. Waiting {wait_seconds} seconds...")
            time.sleep(wait_seconds)

        else:
            response.raise_for_status()

    print("Could not fetch papers due to repeated rate limiting.")
    return []

# def show_papers(papers):
#     for i, paper in enumerate(papers, start=1):
#         authors = ", ".join(a["name"] for a in paper.get("authors", []))

#         print(f"\nPaper {i}")
#         print("Title:", paper.get("title"))
#         print("Authors:", authors)
#         print("Year:", paper.get("year"))
#         print("\nAbstract:")
#         print(paper.get("abstract"))
#         print("\nPaper Link:", paper.get("url"))
#         print("-" * 60)

# topic = "deepfake"
# print("Fetching papers...")
# papers = fetch_papers(topic)
# show_papers(papers)

# def prepare_dataset(papers):
#     dataset = []

#     for paper in papers:
#         record = {
#             "title": paper.get("title"),
#             "authors": [a["name"] for a in paper.get("authors", [])],
#             "year": paper.get("year"),
#             "abstract": paper.get("abstract"),
#             "paper_url": paper.get("url")
#         }

#         dataset.append(record)

#     return dataset

# dataset = prepare_dataset(papers)
# print("-------------------------------------------------------")
# print(dataset)