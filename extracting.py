import os
import fitz  # PyMuPDF

TEXT_DIR = "data/texts"
os.makedirs(TEXT_DIR, exist_ok=True)

def extract_text_from_pdf(pdf_path, paper_id):
    doc = fitz.open(pdf_path)
    text = ""

    for page in doc:
        text += page.get_text()

    file_path = os.path.join(TEXT_DIR, f"{paper_id}.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)

    return file_path
