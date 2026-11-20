# HireSense AI – AI-Powered Resume Screening System

HireSense AI is an intelligent recruitment platform designed to simplify resume screening and candidate evaluation. It helps recruiters analyze multiple resumes against job requirements using Natural Language Processing (NLP), semantic similarity and AI-powered feedback.

The system evaluates candidate profiles, identifies missing skills and generates meaningful feedback to support better recruitment decisions.

## Key Features

- **Recruiter Authentication:** Secure recruiter registration and login.
- **Job Management:** Create, view and manage job postings.
- **Multiple Resume Upload:** Upload and process multiple PDF resumes.
- **Resume Parsing:** Extract candidate information and skills from resumes.
- **Skill Matching:** Compare candidate skills against job requirements.
- **TF-IDF Analysis:** Measure textual relevance between resumes and job descriptions.
- **Semantic Matching:** Use Sentence-BERT to understand contextual similarity.
- **AI-Powered Feedback:** Generate candidate feedback using the Gemini API.
- **Missing Skill Detection:** Identify skills required by a job but missing from a candidate's resume.
- **Candidate Management:** View candidate profiles, screening results and application statuses.
- **Recruitment Dashboard:** Monitor jobs, applicants and screening statistics.

## Technologies Used

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Backend | Flask |
| Frontend | HTML, CSS, JavaScript, Bootstrap |
| Database | MySQL |
| ORM | SQLAlchemy |
| NLP | TF-IDF, Sentence-BERT |
| AI Integration | Google Gemini API |
| PDF Processing | Python PDF extraction libraries |
| Development Tools | VS Code, Git, GitHub |

## AI Resume Screening Workflow

1. Recruiter registers and logs into the platform.
2. Recruiter creates a job posting with required and preferred skills.
3. Recruiter uploads candidate resumes in PDF format.
4. The system extracts resume information and candidate skills.
5. Skill matching evaluates candidate qualifications against job requirements.
6. TF-IDF and Sentence-BERT analyze resume relevance.
7. The system calculates screening scores.
8. Gemini generates AI-powered feedback and improvement suggestions.
9. Recruiters review candidate profiles and make recruitment decisions.

## Project Structure


HireSense-AI/
│
├── app.py
├── config.py
├── extensions.py
├── models.py
├── requirements.txt
│
├── gemini_feedback.py
├── resume_extractor.py
├── resume_parser.py
├── scoring_engine.py
├── screening.py
├── semantic_matcher.py
├── skill_matcher.py
├── tfidf_matcher.py
│
├── templates/
├── static/
│
├── test_db.py
├── test_extractor.py
├── test_models.py
├── test_parser.py
├── test_scoring_engine.py
├── test_semantic.py
├── test_skill_matcher.py
└── test_tfidf.py

Installation and Setup

1. Clone the Repository

git clone https://github.com/meghanahn-29/HireSense-AI.git

2. Navigate to the Project

cd HireSense-AI

3. Create a Virtual Environment

python -m venv venv

Activate it on Windows:

venv\Scripts\activate

4. Install Dependencies

pip install -r requirements.txt

5. Configure Environment Variables

Create a .env file in the project root directory.

Configure the required database credentials, Flask secret key and Gemini API key.

Use the exact environment variable names expected by the application's configuration files.

Important: Never upload your .env file or expose API keys and passwords publicly.

6. Configure the Database

Install and start MySQL.

Create the database configured in your application and ensure the database connection settings are correctly configured.

7. Run the Application

python app.py

Open your browser and visit:

http://127.0.0.1:5000/

Security

Environment variables are used for sensitive configuration.

API keys and database credentials should not be committed to GitHub.

Uploaded resumes and local database files are excluded from version control.

PDF uploads are validated before processing.

Future Enhancements

Advanced candidate ranking and recommendation.

Recruiter analytics and reporting.

Improved resume evaluation models.

Enhanced candidate comparison features.

Author

Meghana H N

BE – Information Science and Engineering

Interested in Python Full Stack Development and AI-powered applications.

HireSense AI – Making Recruitment Smarter with AI.
