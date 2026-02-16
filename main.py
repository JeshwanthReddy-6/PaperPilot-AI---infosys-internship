from fetching import fetch_papers
from download import download_pdf
from key_finding import extract_key_findings
from extracting import extract_text_from_pdf
from utils import clear_data_folders
import os
import json

def run_pipeline(topic,limit):
    clear_data_folders()
    papers = fetch_papers(topic,limit)

    #Create metadata folder
    os.makedirs("data/metadata", exist_ok=True)
    fetched_count = len(papers)
    downloaded_count = 0
    pdf_list = []
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
        downloaded_count += 1
        pdf_list.append(pdf_path)

        extract_text_from_pdf(pdf_path, paper_id)
        extract_key_findings()
    return fetched_count, downloaded_count, pdf_list

# if __name__ == "__main__":
#     run_pipeline("Vision-Based Anomaly Detection System",5)
