# ==========================================
# HIRESENSE AI - TF-IDF MATCHING ENGINE
# ==========================================
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def normalize_text(text):

    synonym_map = {
        "programmer": "developer",
        "programmers": "developers",
        "building web applications": "web application development",
        "backend endpoints": "rest api"
    }

    text = text.lower()

    for original, replacement in synonym_map.items():
        text = re.sub(
            r"\b" + re.escape(original) + r"\b",
            replacement,
            text
        )

    return text


def calculate_tfidf_similarity(resume_text, job_description):

    # Validate input.
    if not resume_text or not job_description:
        return 0.0

    resume_text = resume_text.strip()
    job_description = job_description.strip()

    if not resume_text or not job_description:
        return 0.0

    # Normalize resume and job description.
    resume_text = normalize_text(resume_text)
    job_description = normalize_text(job_description)

    # Prepare both documents.
    documents = [
        resume_text,
        job_description
    ]

    # Convert text into TF-IDF vectors.
    vectorizer = TfidfVectorizer(
        stop_words='english',
        ngram_range=(1, 2)
    )

    tfidf_matrix = vectorizer.fit_transform(documents)

    # Calculate cosine similarity.
    similarity = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:2]
    )[0][0]

    # Convert similarity into percentage.
    score = similarity * 100

    return round(float(score), 2)