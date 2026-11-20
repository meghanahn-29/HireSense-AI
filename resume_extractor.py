import re

SKILLS_LIST = [
    "Python", "Java", "C", "C++", "C#", "JavaScript",
    "HTML", "CSS", "SQL", "MySQL", "SQLite",
    "Flask", "Django", "FastAPI", "React", "Angular",
    "Bootstrap", "Node.js", "Express.js",
    "Machine Learning", "Deep Learning", "NLP",
    "Scikit-learn", "TensorFlow", "PyTorch",
    "Pandas", "NumPy", "OpenCV",
    "Git", "GitHub", "Docker", "AWS", "Azure",
    "REST API", "REST APIs", "SQLAlchemy",
    "MongoDB", "PostgreSQL",
    "Data Structures", "OOP"
]


def extract_email(text):
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    match = re.search(pattern, text)
    return match.group(0) if match else None


def extract_phone(text):
    pattern = r'(?<!\d)(?:\+91[\s-]?)?[6-9](?:[\s-]?\d){9}(?!\d)'
    match = re.search(pattern, text)
    return match.group(0) if match else None

def extract_location(text):
    header = text[:500]

    pattern = r'\b([A-Z][a-z]+,\s*[A-Z][a-z]+)(?=\s*\|)'

    match = re.search(pattern, header)

    return match.group(1).strip() if match else None


def extract_name(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    if not lines:
        return None

    for line in lines[:5]:
        cleaned = re.sub(r'[^A-Za-z .-]', '', line).strip()

        if (
            cleaned
            and len(cleaned.split()) >= 2
            and len(cleaned) <= 60
            and not any(
                word in cleaned.lower()
                for word in ["student", "developer", "engineer", "resume"]
            )
        ):
            return cleaned

    return None


def extract_skills(text):

    found_skills = []

    negative_context = [
        r"interested in learning",
        r"currently learning",
        r"learning",
        r"no experience with",
        r"no knowledge of",
        r"not experienced in",
        r"not familiar with",
        r"unfamiliar with",
        r"do not know",
        r"don't know",
        r"have never worked with",
        r"never used"
    ]

    for skill in SKILLS_LIST:

        pattern = (
            r'(?<![A-Za-z0-9])'
            + re.escape(skill)
            + r'(?![A-Za-z0-9])'
        )

        matches = re.finditer(pattern, text, re.IGNORECASE)

        for match in matches:

            # Get the sentence containing the skill.
            sentence_start = max(
                text.rfind(".", 0, match.start()),
                text.rfind("\n", 0, match.start())
            ) + 1

            sentence_end = text.find(".", match.end())

            if sentence_end == -1:
                sentence_end = len(text)

            sentence = text[sentence_start:sentence_end].lower()

            # Check whether the skill is mentioned negatively.
            skill_position = match.start() - sentence_start

            preceding_text = sentence[:skill_position].strip()

            is_negative = any(
                re.search(phrase + r'\s*$', preceding_text)
                for phrase in negative_context
            )

            if not is_negative:
                found_skills.append(skill)
                break

    return found_skills

    for skill in SKILLS_LIST:
        pattern = (
            r'(?<![A-Za-z0-9])'
            + re.escape(skill)
            + r'(?![A-Za-z0-9])'
        )

        if re.search(pattern, text, re.IGNORECASE):
            found_skills.append(skill)

    return found_skills


def extract_education(text):

    education_patterns = {
        "B.E.": r"\bB\.?\s*E\.?\b",
        "B.Tech": r"\bB\.?\s*Tech\.?\b",
        "Bachelor": r"\bBachelor(?:'s)?\b",
        "M.E.": r"\bM\.?\s*E\.?\b",
        "M.Tech": r"\bM\.?\s*Tech\.?\b",
        "Master": r"\bMaster(?:'s)?\b",
        "BCA": r"\bB\.?\s*C\.?\s*A\.?\b",
        "MCA": r"\bM\.?\s*C\.?\s*A\.?\b",
        "B.Sc": r"\bB\.?\s*Sc\.?\b",
        "M.Sc": r"\bM\.?\s*Sc\.?\b",
        "PUC": r"\bPUC\b",
        "Diploma": r"\bDiploma\b",
        "Ph.D": r"\bPh\.?\s*D\.?\b"
    }

    found_education = []

    for qualification, pattern in education_patterns.items():

        if re.search(pattern, text, re.IGNORECASE):
            found_education.append(qualification)

    return found_education


def extract_cgpa(text):

    pattern =r'\b(?:CGPA|GPA)\s*[:\-]?\s*(\d{1,2}(?:\.\d{1,2})?)'

    match = re.search(pattern, text, re.IGNORECASE)

    if not match:
        return None

    cgpa = float(match.group(1))

    # Validate CGPA on a 10-point scale.
    if 0 <= cgpa <= 10:
        return cgpa

    return None


def extract_resume_information(text):
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "education": extract_education(text),
        "cgpa": extract_cgpa(text),
        "location": extract_location(text),
    }