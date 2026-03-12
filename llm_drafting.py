from groq import Groq
from secrects import GROQ_API_KEY
import os
import json

client = Groq(api_key=GROQ_API_KEY)

def load_all_findings_with_metadata(session_id, selected_paper_ids=None):
    """
    Load findings from papers.
    If selected_paper_ids is provided, only load those papers.
    If None, load all papers.
    """
    combined = ""
    dist_dir = f"user_sessions/{session_id}/dist_texts"
    meta_dir = f"user_sessions/{session_id}/metadata"

    if not os.path.exists(dist_dir):
        return combined

    for file in os.listdir(dist_dir):
        if not file.endswith("_findings.txt"):
            continue

        paper_id = file.replace("_findings.txt", "")
        
        # If specific papers are selected, skip others
        if selected_paper_ids is not None and paper_id not in selected_paper_ids:
            continue
        
        meta_path = f"{meta_dir}/{paper_id}.json"
        findings_path = f"{dist_dir}/{file}"

        if not os.path.exists(meta_path):
            continue

        with open(meta_path, "r", encoding="utf-8") as m:
            meta = json.load(m)

        with open(findings_path, "r", encoding="utf-8") as f:
            findings = f.read().strip()

        if not findings:
            continue

        combined += f"""
Paper:
Title: {meta['title']}
Authors: {", ".join(meta['authors'])}
Year: {meta['year']}
URL: {meta['paper_url']}

Key Findings:
{findings}
"""
    return combined


def generate_synthesized_paper(session_id, selected_paper_ids=None):
    content = load_all_findings_with_metadata(session_id, selected_paper_ids)
    if not content.strip():
        raise ValueError("No key findings found for selected papers. Cannot generate synthesized paper.")
    
    prompt = f"""
You are an academic research assistant.

Using the following key findings extracted from multiple research papers on the same topic, generate a SINGLE synthesized research paper draft based ONLY on the provided content.

STRICT FORMAT - Follow this EXACT structure with NO markdown symbols (no **, no ##, no *):

[Write a clear title for the paper here]

Abstract
[Write the abstract paragraph here - summarize the key themes and findings]

Methods
[Write the methods section here - describe the approaches used across papers]

Results
[Write the results section here - synthesize the main findings]

References
[List all references in APA style, one per line]

CONTENT RULES:
- Do NOT use any markdown formatting like **, ##, *, or similar symbols
- Do NOT wrap section headers in any special characters
- Section headers should be plain text on their own line (Abstract, Methods, Results, References)
- Do not invent new information
- Base everything strictly on the input
- Use academic tone
- Do NOT include numerical values, percentages, model sizes, dataset sizes
- Replace quantitative claims with qualitative academic language
- Do NOT use first-person language ("we", "our")

Key Findings and Metadata:
{content}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content


def call_function(session_id, selected_paper_ids=None):
    """
    Generate synthesized paper.
    If selected_paper_ids is provided, only use those papers.
    """
    paper = generate_synthesized_paper(session_id, selected_paper_ids)
    output_dir = f"user_sessions/{session_id}/output"
    os.makedirs(output_dir, exist_ok=True)

    with open(f"{output_dir}/synthesized_paper.txt", "w", encoding="utf-8") as f:
        f.write(paper)
    return paper