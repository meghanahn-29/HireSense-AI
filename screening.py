from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SKILLS = [
    'python',
    'flask',
    'sql',
    'html',
    'css',
    'javascript',
    'machine learning',
    'data analysis',
    'java',
    'c++',
    'mysql',
    'git'
]


def extract_skills(text):

    found_skills = []

    text = text.lower()

    for skill in SKILLS:

        if skill in text:
            found_skills.append(skill.title())

    return found_skills


def calculate_similarity(job_description, resume_text):

    documents = [job_description, resume_text]

    tfidf = TfidfVectorizer()

    tfidf_matrix = tfidf.fit_transform(documents)

    similarity = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:2]
    )

    score = similarity[0][0] * 100

    return score