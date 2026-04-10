from fetching import fetch_papers
from download import download_pdf
from key_finding import extract_key_findings
from extracting import extract_text_from_pdf
from utils import clear_data_folders
import os
import json

def run_pipeline(topic, limit, session_id):
    clear_data_folders(session_id)
    papers = fetch_papers(topic, limit)

    metadata_dir = f"user_sessions/{session_id}/metadata"
    os.makedirs(metadata_dir, exist_ok=True)

    fetched_count = len(papers)
    downloaded_count = 0
    pdf_list = []

    for paper in papers:
        paper_id = paper.get("paperId")
        if not paper_id:
            continue

        open_access_pdf = paper.get("openAccessPdf")
        pdf_url = None

        if open_access_pdf and isinstance(open_access_pdf, dict):
            pdf_url = open_access_pdf.get("url")

        if not pdf_url:
            print(f"No PDF available for paper id - {paper_id}")
            continue

        # Try downloading first
        pdf_path = download_pdf(pdf_url, paper_id, session_id)
        if not pdf_path:
            continue

        # Save metadata ONLY if PDF is actually downloadable
        metadata = {
            "paperId": paper_id,
            "title": paper.get("title"),
            "authors": [a["name"] for a in paper.get("authors", [])],
            "year": paper.get("year"),
            "paper_url": paper.get("url")
        }

        with open(f"{metadata_dir}/{paper_id}.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        downloaded_count += 1
        pdf_list.append(pdf_path)

        try:
            extract_text_from_pdf(pdf_path, paper_id, session_id)
        except Exception as e:
            print(f"Text extraction failed for paper id - {paper_id}: {e}")
            continue

    # Run key findings extraction once after all texts are ready
    try:
        extract_key_findings(session_id)
    except Exception as e:
        print(f"Key findings extraction failed: {e}")

    return fetched_count, downloaded_count, pdf_list