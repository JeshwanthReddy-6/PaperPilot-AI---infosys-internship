import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def load_documents(session_id):
    KEY_FINDINGS_DIR = f"user_sessions/{session_id}/dist_texts"
    documents = []
    doc_names = []

    if not os.path.exists(KEY_FINDINGS_DIR):
        return documents, doc_names

    for filename in os.listdir(KEY_FINDINGS_DIR):
        if not filename.endswith("_findings.txt"):
            continue

        path = os.path.join(KEY_FINDINGS_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read().strip()

        # skip empty papers
        if text:
            documents.append(text)
            doc_names.append(filename)

    return documents, doc_names


def compute_similarity(session_id):
    documents, doc_names = load_documents(session_id)
    if len(documents) < 2:
        return "Not enough documents for comparison."

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)
    similarity_matrix = cosine_similarity(tfidf_matrix)

    result = "Cosine Similarity Matrix:\n\n"
    for i in range(len(doc_names)):
        for j in range(i + 1, len(doc_names)):
            result += (
                f"{doc_names[i]}  vs  {doc_names[j]}  →  "
                f"{similarity_matrix[i][j]:.3f}\n"
            )

    return result