from extensions import db
from sqlalchemy.dialects.mysql import LONGTEXT


# 1. RECRUITER
class Recruiter(db.Model):
    __tablename__ = 'recruiters'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    jobs = db.relationship('Job', back_populates='recruiter')


# 2. CANDIDATE
class Candidate(db.Model):
    __tablename__ = 'candidates'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    location = db.Column(db.String(150))
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    applications = db.relationship(
        'Application',
        back_populates='candidate'
    )

    resumes = db.relationship(
        'Resume',
        back_populates='candidate'
    )

    candidate_skills = db.relationship(
        'CandidateSkill',
        back_populates='candidate'
    )


# 3. JOB
class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    recruiter_id = db.Column(
        db.Integer,
        db.ForeignKey('recruiters.id'),
        nullable=False
    )
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(150))
    employment_type = db.Column(db.String(50))
    min_experience_years = db.Column(db.Numeric(4, 1))
    education = db.Column(db.String(150))
    status = db.Column(db.String(30), default='Active')
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    recruiter = db.relationship(
        'Recruiter',
        back_populates='jobs'
    )

    applications = db.relationship(
        'Application',
        back_populates='job'
    )

    job_skills = db.relationship(
        'JobSkill',
        back_populates='job'
    )


# 4. APPLICATION
class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(
        db.Integer,
        db.ForeignKey('candidates.id'),
        nullable=False
    )
    job_id = db.Column(
        db.Integer,
        db.ForeignKey('jobs.id'),
        nullable=False
    )
    status = db.Column(db.String(30), default='Pending')
    applied_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    candidate = db.relationship(
        'Candidate',
        back_populates='applications'
    )

    job = db.relationship(
        'Job',
        back_populates='applications'
    )

    analyses = db.relationship(
        'ResumeAnalysis',
        back_populates='application'
    )

    # NEW: Application-to-resume relationship
    resumes = db.relationship(
        'Resume',
        back_populates='application'
    )


# 5. RESUME
class Resume(db.Model):
    __tablename__ = 'resumes'

    id = db.Column(db.Integer, primary_key=True)

    candidate_id = db.Column(
        db.Integer,
        db.ForeignKey('candidates.id'),
        nullable=False
    )

    # NEW: Connect resume to its specific application
    application_id = db.Column(
        db.Integer,
        db.ForeignKey('applications.id'),
        nullable=True
    )

    original_filename = db.Column(db.String(255))
    stored_filename = db.Column(db.String(255))
    file_path = db.Column(db.String(500))
    extracted_text = db.Column(LONGTEXT)

    uploaded_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    candidate = db.relationship(
        'Candidate',
        back_populates='resumes'
    )

    # NEW: Resume-to-application relationship
    application = db.relationship(
        'Application',
        back_populates='resumes'
    )


# 6. SKILL
class Skill(db.Model):
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    skill_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100))

    candidate_skills = db.relationship(
        'CandidateSkill',
        back_populates='skill'
    )

    job_skills = db.relationship(
        'JobSkill',
        back_populates='skill'
    )


# 7. CANDIDATE SKILL
class CandidateSkill(db.Model):
    __tablename__ = 'candidate_skills'

    id = db.Column(db.Integer, primary_key=True)

    candidate_id = db.Column(
        db.Integer,
        db.ForeignKey('candidates.id'),
        nullable=False
    )

    skill_id = db.Column(
        db.Integer,
        db.ForeignKey('skills.id'),
        nullable=False
    )

    evidence = db.Column(db.Text)

    candidate = db.relationship(
        'Candidate',
        back_populates='candidate_skills'
    )

    skill = db.relationship(
        'Skill',
        back_populates='candidate_skills'
    )


# 8. JOB SKILL
class JobSkill(db.Model):
    __tablename__ = 'job_skills'

    id = db.Column(db.Integer, primary_key=True)

    job_id = db.Column(
        db.Integer,
        db.ForeignKey('jobs.id'),
        nullable=False
    )

    skill_id = db.Column(
        db.Integer,
        db.ForeignKey('skills.id'),
        nullable=False
    )

    is_required = db.Column(db.Boolean, default=True)

    job = db.relationship(
        'Job',
        back_populates='job_skills'
    )

    skill = db.relationship(
        'Skill',
        back_populates='job_skills'
    )


# 9. RESUME ANALYSIS
class ResumeAnalysis(db.Model):
    __tablename__ = 'resume_analyses'

    id = db.Column(db.Integer, primary_key=True)

    application_id = db.Column(
        db.Integer,
        db.ForeignKey('applications.id'),
        nullable=False
    )

    tfidf_score = db.Column(db.Numeric(5, 2))
    semantic_score = db.Column(db.Numeric(5, 2))
    skill_match_score = db.Column(db.Numeric(5, 2))
    experience_score = db.Column(db.Numeric(5, 2))
    overall_score = db.Column(db.Numeric(5, 2))

    analysis_date = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    model_version = db.Column(db.String(100))

    application = db.relationship(
        'Application',
        back_populates='analyses'
    )

    feedback = db.relationship(
        'Feedback',
        back_populates='analysis'
    )


# 10. FEEDBACK
class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)

    analysis_id = db.Column(
        db.Integer,
        db.ForeignKey('resume_analyses.id'),
        nullable=False
    )

    feedback_text = db.Column(LONGTEXT, nullable=False)
    generated_by = db.Column(db.String(50), default='Gemini')

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    analysis = db.relationship(
        'ResumeAnalysis',
        back_populates='feedback'
    )