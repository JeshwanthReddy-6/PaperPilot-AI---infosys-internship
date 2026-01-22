import os
import requests

PDF_DIR = "data/pdfs"
os.makedirs(PDF_DIR, exist_ok=True)

def download_pdf(pdf_url, paper_id):
    try:
        response = requests.get(pdf_url, timeout=15)
        response.raise_for_status()

        file_path = os.path.join(PDF_DIR, f"{paper_id}.pdf")
        with open(file_path, "wb") as f:
            f.write(response.content)

        return file_path

    except Exception as e:
        print(f"Failed to download PDF for paper id - {paper_id} due to error - {e}")
        return None
