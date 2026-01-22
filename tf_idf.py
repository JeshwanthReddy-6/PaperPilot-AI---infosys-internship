import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

KEY_FINDINGS_DIR = "data/dist_texts"

def load_documents():
    documents = []
    doc_names = []

    for filename in os.listdir(KEY_FINDINGS_DIR):
        if not filename.endswith("_findings.txt"):
            continue

        path = os.path.join(KEY_FINDINGS_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read().strip()

        # skip empty papers (important)
        if text:
            documents.append(text)
            doc_names.append(filename)

    return documents, doc_names


def compute_similarity():
    documents, doc_names = load_documents()
    if len(documents) < 2:
        print("Not enough documents for comparison.")
        return

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    tfidf_matrix = vectorizer.fit_transform(documents)

    similarity_matrix = cosine_similarity(tfidf_matrix)

    print("\n--- Cosine Similarity Matrix ---\n")
    for i in range(len(doc_names)):
        for j in range(i + 1, len(doc_names)):
            print(
                f"{doc_names[i]}  vs  {doc_names[j]}  →  "
                f"{similarity_matrix[i][j]:.3f}"
            )

compute_similarity()