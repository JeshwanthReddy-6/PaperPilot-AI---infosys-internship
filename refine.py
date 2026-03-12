from groq import Groq
from secrects import GROQ_API_KEY
from pdf_convert import text_to_pdf
import os

client = Groq(api_key=GROQ_API_KEY)

def refine_synthesized_paper(existing_paper, instruction, session_id):
    prompt = f"""
You are an academic editor.

Below is a synthesized research paper.
The user has requested the following customization:

"{instruction}"

Apply ONLY this customization.

STRICT RULES:
- Do NOT invent new information.
- Do NOT add new references.
- Preserve the EXACT same structure (Title, Abstract, Methods, Results, References).
- Return the FULL updated paper.
- Do NOT explain changes.
- Do NOT use any markdown formatting like **, ##, *, or similar symbols.
- Keep section headers as plain text (Abstract, Methods, Results, References).
- Do NOT wrap any text in special characters.

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
    output_dir = f"user_sessions/{session_id}/output"
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = f"{output_dir}/synthesized_paper.pdf"
    text_to_pdf(refined_text, pdf_path)

    return refined_text, pdf_path