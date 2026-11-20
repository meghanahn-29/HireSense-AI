from app import app
from models import (
    Recruiter,
    Candidate,
    Job,
    Application,
    Resume,
    Skill,
    CandidateSkill,
    JobSkill,
    ResumeAnalysis,
    Feedback
)

with app.app_context():

    print("HireSense AI Model Verification")

    models = [
        Recruiter,
        Candidate,
        Job,
        Application,
        Resume,
        Skill,
        CandidateSkill,
        JobSkill,
        ResumeAnalysis,
        Feedback
    ]

    for model in models:
        print(
            model.__name__,
            "->",
            model.__tablename__
        )

    print("\nAll 10 models imported successfully!")