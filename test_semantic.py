from semantic_matcher import calculate_semantic_similarity


# Sample candidate resume.
resume_text = """
I have no experience with Python.
I am not familiar with Flask.
I have never worked with MySQL.
I do not know REST API development.
"""

# Sample job description.
job_description = """
We are looking for a Python Full Stack Developer.
Required skills include Python, Flask and MySQL.
The candidate should know REST API development,
HTML, CSS, JavaScript and database management.
"""


# Calculate semantic similarity.
score = calculate_semantic_similarity(
    resume_text,
    job_description
)


print("\n========== HIRESENSE AI ==========")
print("   SEMANTIC MATCHING RESULTS")
print("==================================")

print("Sentence-BERT Similarity Score:", score, "%")

print("==================================")