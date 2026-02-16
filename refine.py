from groq import Groq
from secrects import GROQ_API_KEY
from pdf_convert import text_to_pdf
import os

client = Groq(api_key=GROQ_API_KEY)

def refine_synthesized_paper(existing_paper, instruction):
    prompt = f"""
You are an academic editor.

Below is a synthesized research paper.
The user has requested the following customization:

"{instruction}"

Apply ONLY this customization.

Rules:
- Do NOT invent new information.
- Do NOT add new references.
- Preserve APA-style structure.
- Return the FULL updated paper.
- Do NOT explain changes.

Paper:
{existing_paper}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    refined_text = response.choices[0].message.content

    # regenerate PDF
    os.makedirs("data/output", exist_ok=True)
    pdf_path = "data/output/synthesized_paper.pdf"
    text_to_pdf(refined_text, pdf_path)

    return refined_text, pdf_path
