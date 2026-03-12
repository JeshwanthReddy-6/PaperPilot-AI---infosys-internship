import os
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path, paper_id, session_id):
    TEXT_DIR = f"user_sessions/{session_id}/texts"
    os.makedirs(TEXT_DIR, exist_ok=True)
    
    doc = fitz.open(pdf_path)
    text = ""

    for page in doc:
        text += page.get_text()

    file_path = os.path.join(TEXT_DIR, f"{paper_id}.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)

    return file_path