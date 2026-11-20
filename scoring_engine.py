# ==========================================
# HIRESENSE AI - OVERALL SCORING ENGINE
# ==========================================

def calculate_overall_score(
    skill_match_score,
    tfidf_score,
    semantic_score
):

    # Initial experimental weights
    SKILL_WEIGHT = 0.40
    TFIDF_WEIGHT = 0.20
    SEMANTIC_WEIGHT = 0.40

    # Validate input scores
    scores = [
        skill_match_score,
        tfidf_score,
        semantic_score
    ]

    for score in scores:
        if not isinstance(score, (int, float)):
            raise ValueError("Scores must be numeric.")

        if not 0 <= score <= 100:
            raise ValueError("Scores must be between 0 and 100.")

    # Calculate overall score
    overall_score = (
        skill_match_score * SKILL_WEIGHT
        + tfidf_score * TFIDF_WEIGHT
        + semantic_score * SEMANTIC_WEIGHT
    )

    return round(overall_score, 2)