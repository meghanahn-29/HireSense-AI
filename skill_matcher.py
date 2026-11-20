# ==========================================
# HIRESENSE AI - SKILL MATCHING ENGINE
# ==========================================

# Standard names for commonly used skill abbreviations
SKILL_ALIASES = {
    "js": "javascript",
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "sklearn": "scikit-learn",
    "nodejs": "node.js",
    "rest apis": "rest api"
}


# Normalize individual skill names
def normalize_skill(skill):

    if not skill:
        return ""

    skill = " ".join(skill.strip().lower().split())

    return SKILL_ALIASES.get(skill, skill)


# Calculate skill matching score
def calculate_skill_match(candidate_skills, job_skills):

    # Normalize candidate skills
    candidate_skills = {
        normalize_skill(skill)
        for skill in candidate_skills
        if skill and skill.strip()
    }

    # Separate required and preferred skills
    required_skills = {
        normalize_skill(skill)
        for skill, is_required in job_skills
        if is_required and skill and skill.strip()
    }

    preferred_skills = {
        normalize_skill(skill)
        for skill, is_required in job_skills
        if not is_required and skill and skill.strip()
    }

    # Match required skills
    matched_required = candidate_skills.intersection(
        required_skills
    )

    missing_required = required_skills.difference(
        candidate_skills
    )

    # Match preferred skills
    matched_preferred = candidate_skills.intersection(
        preferred_skills
    )

    missing_preferred = preferred_skills.difference(
        candidate_skills
    )

    # Calculate required skill coverage
    if required_skills:

        skill_match_score = (
            len(matched_required) / len(required_skills)
        ) * 100

    else:

        skill_match_score = 0

    # Generate improvement suggestions
    improvement_suggestions = [
        f"Consider improving your knowledge of {skill}."
        for skill in sorted(missing_required)
    ]

    return {

        "skill_match_score": round(skill_match_score, 2),

        "matched_required_skills": sorted(matched_required),

        "missing_required_skills": sorted(missing_required),

        "matched_preferred_skills": sorted(matched_preferred),

        "missing_preferred_skills": sorted(missing_preferred),

        "total_required_skills": len(required_skills),

        "matched_required_count": len(matched_required),

        "total_preferred_skills": len(preferred_skills),

        "matched_preferred_count": len(matched_preferred),

        "improvement_suggestions": improvement_suggestions

    }