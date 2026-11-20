# ==========================================
# HIRESENSE AI - SEMANTIC MATCHING ENGINE
# ==========================================

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# Load the pretrained Sentence-BERT model.
model = SentenceTransformer('all-MiniLM-L6-v2')


def calculate_semantic_similarity(resume_text, job_description):

    # Validate input.
    if not resume_text or not job_description:
        return 0.0

    resume_text = resume_text.strip()
    job_description = job_description.strip()

    if not resume_text or not job_description:
        return 0.0

    # Generate semantic embeddings.
    embeddings = model.encode([
        resume_text,
        job_description
    ])

    # Calculate cosine similarity.
    similarity = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]]
    )[0][0]

    # Convert similarity into percentage.
    score = float(similarity) * 100

    return round(score, 2)