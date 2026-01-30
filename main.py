from fetching import fetch_papers
from download import download_pdf
from extracting import extract_text_from_pdf
import os
import json

def run_pipeline(topic):
    papers = fetch_papers(topic)

    #Create metadata folder
    os.makedirs("data/metadata", exist_ok=True)

    for paper in papers:
        paper_id = paper.get("paperId")

        #SAVE METADATA (once per paper)
        metadata = {
            "paperId": paper_id,
            "title": paper.get("title"),
            "authors": [a["name"] for a in paper.get("authors", [])],
            "year": paper.get("year"),
            "paper_url": paper.get("url")
        }

        with open(f"data/metadata/{paper_id}.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        pdf_url = paper.get("openAccessPdf", {}).get("url")

        if not pdf_url:
            print(f"No PDF available for paper id - {paper_id}")
            continue

        pdf_path = download_pdf(pdf_url, paper_id)
        if not pdf_path:
            continue

        extract_text_from_pdf(pdf_path, paper_id)

if __name__ == "__main__":
    run_pipeline("deepfake")
