
import os
import re
import logging
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types


# Load environment variables
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

GEMINI_MODEL = "gemini-3.1-flash-lite"
logger = logging.getLogger(__name__)


def remove_personal_information(text):
    """Remove email addresses and phone numbers."""

    text = re.sub(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
        '[EMAIL REMOVED]',
        text
    )

    text = re.sub(
        r'(?<!\d)(?:\+91[\s-]?)?[6-9](?:[\s-]?\d){9}(?!\d)',
        '[PHONE REMOVED]',
        text
    )

    return text


def generate_fallback_feedback(
    resume_text,
    required_skills,
    preferred_skills,
    skill_match_score,
    tfidf_score,
    semantic_score,
    overall_score
):
    """Generate feedback when Gemini is unavailable."""

    resume_lower = resume_text.lower()

    matched_required = [
        skill for skill in required_skills
        if re.search(
            r'(?<!\w)' + re.escape(skill.lower()) + r'(?!\w)',
            resume_lower
        )
    ]

    missing_required = [
        skill for skill in required_skills
        if skill not in matched_required
    ]

    matched_preferred = [
        skill for skill in preferred_skills
        if re.search(
            r'(?<!\w)' + re.escape(skill.lower()) + r'(?!\w)',
            resume_lower
        )
    ]

    missing_preferred = [
        skill for skill in preferred_skills
        if skill not in matched_preferred
    ]

    feedback = f"""
RULE-BASED CANDIDATE FEEDBACK
(Generated without Gemini API)

1. CANDIDATE STRENGTHS

Required skills identified:
{', '.join(matched_required) if matched_required else 'No required skills identified.'}

Preferred skills identified:
{', '.join(matched_preferred) if matched_preferred else 'No preferred skills identified.'}


2. MISSING REQUIRED SKILLS

{', '.join(missing_required) if missing_required else 'No missing required skills identified.'}


3. MISSING PREFERRED SKILLS

{', '.join(missing_preferred) if missing_preferred else 'No missing preferred skills identified.'}


4. SCREENING SCORES

Skill Match Score: {skill_match_score}%
TF-IDF Similarity: {tfidf_score}%
Semantic Similarity: {semantic_score}%
Overall Score: {overall_score}%


5. IMPROVEMENT SUGGESTIONS

- Add relevant projects demonstrating the required technical skills.
- Include practical examples of how technical skills were used.
- Improve the description of project responsibilities and achievements.
- Add evidence of missing required skills if those skills have been learned.


6. OVERALL RECRUITER RECOMMENDATION

The resume has been evaluated using automated skill matching and text similarity scores.

A recruiter should manually review the candidate's experience, projects, and technical knowledge before making a final hiring decision.


Note: This feedback was generated using rule-based matching because Gemini feedback was unavailable. Skill matching is based on resume text and does not prove actual proficiency.
"""

    return feedback.strip()


def generate_resume_feedback(
    resume_text,
    job_title,
    job_description,
    required_skills,
    preferred_skills,
    skill_match_score,
    tfidf_score,
    semantic_score,
    overall_score
):
    """Generate job-specific feedback using Gemini with fallback."""

    try:

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=20000)
        )

        safe_resume_text = remove_personal_information(resume_text)

        prompt = f"""
You are an experienced technical recruiter and resume analyst.

Analyze the candidate's resume against the following job.

JOB TITLE:
{job_title}

JOB DESCRIPTION:
{job_description}

REQUIRED SKILLS:
{', '.join(required_skills)}

PREFERRED SKILLS:
{', '.join(preferred_skills)}

SCREENING SCORES:
Skill Match: {skill_match_score}%
TF-IDF Similarity: {tfidf_score}%
Semantic Similarity: {semantic_score}%
Overall Score: {overall_score}%

CANDIDATE RESUME:
{safe_resume_text}

Generate a professional, evidence-based candidate feedback report.

Include these sections:

1. Candidate Strengths
2. Relevant Technical Skills
3. Missing Required Skills
4. Areas That Need Improvement
5. Resume Improvement Suggestions
6. Overall Recruiter Recommendation

IMPORTANT RULES:

- Evaluate only job-related qualifications.
- Do not invent skills, experience, or qualifications.
- Identify missing skills accurately.
- Support observations using information from the resume.
- Do not infer personal attributes.
- Do not treat screening scores as proof of candidate ability.
- Do not invent dates or candidate details.
- Keep the feedback clear, specific, and professional.
- If information is unavailable, explicitly mention that.

Return the feedback using readable headings and bullet points.
"""

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )

        if not response.text:
            raise ValueError("Gemini returned an empty response.")

        return {
            "feedback_text": response.text.strip(),
            "generated_by": "Gemini"
        }

    except Exception as error:

        logger.warning(
            "Gemini feedback generation failed: %s",
            error
        )

        fallback_feedback = generate_fallback_feedback(
            resume_text=resume_text,
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            skill_match_score=skill_match_score,
            tfidf_score=tfidf_score,
            semantic_score=semantic_score,
            overall_score=overall_score
        )

        return {
            "feedback_text": fallback_feedback,
            "generated_by": "Rule-Based"
        }
