from tfidf_matcher import normalize_text
from tfidf_matcher import calculate_tfidf_similarity



job_description = """
Python Full Stack Developer.
Required skills: Python, Flask, MySQL,
HTML, CSS, JavaScript and REST API development.
"""


test_cases = {
    "Highly Relevant": (
        """
        Python developer experienced in Flask,
        MySQL, HTML, CSS, JavaScript and REST APIs.
        """,
        job_description
    ),

    "Partially Relevant": (
        """
        Python developer with knowledge of HTML, CSS,
        JavaScript and basic SQL. No experience with Flask
        or REST API development.
        """,
        job_description
    ),

    "Unrelated Resume": (
        """
        Marketing professional experienced in sales,
        advertising, customer relationships and business development.
        """,
        job_description
    ),

    "Keyword Stuffing": (
        """
        Python Python Python Python Python.
        Flask Flask Flask Flask Flask.
        MySQL MySQL MySQL MySQL.
        HTML HTML CSS CSS JavaScript JavaScript.
        """,
        job_description
    ),
    "Synonym Test": (
        """
        Software programmer building web applications
        using Python, Flask, MySQL, HTML, CSS,
        JavaScript and backend endpoints.
        """,
        job_description
    ),
    "Empty Resume": (
        "",
        job_description
    ),

    "Empty Job Description": (
        """
        Python developer with Flask and MySQL experience.
        """,
        ""
    )
}
synonym_resume = """
Software programmer building web applications
using Python, Flask, MySQL, HTML, CSS,
JavaScript and backend endpoints.
"""
print("\n========== NORMALIZED TEXT ==========")

print("\nOriginal Resume:")
print(synonym_resume)

print("\nNormalized Resume:")
print(normalize_text(synonym_resume))

print("\nOriginal Job Description:")
print(job_description)

print("\nNormalized Job Description:")
print(normalize_text(job_description))


print("\n========== TF-IDF EVALUATION ==========\n")

for name, (resume, jd) in test_cases.items():

    score = calculate_tfidf_similarity(
        resume,
        jd
    )

    print(f"{name}: {score}%")

print("\n=======================================")