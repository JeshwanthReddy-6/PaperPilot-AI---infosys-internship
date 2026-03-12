import os
import re

KEY_PHRASES = [
    "we propose",
    "we introduce",
    "our approach",
    "our method",
    "we demonstrate",
    "outperforms",
    "achieves state-of-the-art",
    "this paper proposes",
    "this paper presents",
    "a novel",
    "a new",
    "we present",
    "we develop",
    "we design",
    "is proposed",
    "is presented",
    "the proposed method",
    "the proposed approach",
    "experimental results show",
    "results demonstrate"
]

def extract_key_findings(session_id):
    TEXT_DIR = f"user_sessions/{session_id}/texts"
    OUTPUT_DIR = f"user_sessions/{session_id}/dist_texts"
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for filename in os.listdir(TEXT_DIR):
        if not filename.endswith(".txt"):
            continue

        input_path = os.path.join(TEXT_DIR, filename)
        output_path = os.path.join(
            OUTPUT_DIR,
            filename.replace(".txt", "_findings.txt")
        )

        with open(input_path, "r", encoding="utf-8") as f:
            text = f.read().lower()   

        sentences = re.split(r'(?<=[.!?])\s+', text)

        key_sentences = []
        for sentence in sentences:
            if any(phrase in sentence for phrase in KEY_PHRASES):
                key_sentences.append(sentence.strip())

        with open(output_path, "w", encoding="utf-8") as f:
            for s in key_sentences:
                f.write(s + "\n")

        print(f"Extracted {len(key_sentences)} key findings from {filename}")