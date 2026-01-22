from fetching import fetch_papers
from download import download_pdf
from extracting import extract_text_from_pdf

def run_pipeline(topic):
    papers = fetch_papers(topic)

    for paper in papers:
        paper_id = paper.get("paperId")
        pdf_url = paper.get("openAccessPdf", {}).get("url")

        if not pdf_url:
            print(f"No PDF available for paper id - {paper_id}")
            continue

        pdf_path = download_pdf(pdf_url, paper_id)
        if not pdf_path:
            continue

        extract_text_from_pdf(pdf_path, paper_id)

if __name__ == "__main__":
    run_pipeline("Economics & education")
