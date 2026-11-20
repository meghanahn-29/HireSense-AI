
import os
import uuid
from pathlib import Path

from flask import (
    Flask, render_template, request, redirect,
    session, flash, url_for
)

from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from extensions import db
from config import Config

from models import (
    Recruiter, Candidate, Job, Application, Resume,
    Skill, CandidateSkill, JobSkill, ResumeAnalysis, Feedback
)

from resume_parser import extract_text_from_pdf
from resume_extractor import extract_resume_information
from skill_matcher import calculate_skill_match
from tfidf_matcher import calculate_tfidf_similarity
from semantic_matcher import calculate_semantic_similarity
from scoring_engine import calculate_overall_score
from gemini_feedback import generate_resume_feedback


# --------------------------------------------------
# APPLICATION CONFIGURATION
# --------------------------------------------------

app = Flask(__name__)
app.config.from_object(Config)

BASE_DIR = Path(__file__).resolve().parent

UPLOAD_FOLDER = BASE_DIR / "uploads" / "resumes"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

ALLOWED_EXTENSIONS = {"pdf"}

db.init_app(app)


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def get_logged_in_recruiter():
    recruiter_id = session.get("recruiter_id")

    if not recruiter_id:
        return None

    return db.session.get(Recruiter, recruiter_id)


def get_or_create_skill(skill_name):
    skill_name = skill_name.strip()

    if not skill_name:
        return None

    skill = Skill.query.filter(
        func.lower(Skill.skill_name) == skill_name.lower()
    ).first()

    if skill:
        return skill

    skill = Skill(
        skill_name=skill_name,
        category="Technical"
    )

    db.session.add(skill)
    db.session.flush()

    return skill


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.route("/")
def home():
    if session.get("recruiter_id"):
        return redirect(url_for("dashboard"))

    return render_template("index.html")


# --------------------------------------------------
# RECRUITER REGISTRATION
# --------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("register"))

        if len(password) < 8:
            flash(
                "Password must contain at least 8 characters.",
                "danger"
            )
            return redirect(url_for("register"))

        existing_recruiter = Recruiter.query.filter(
            (func.lower(Recruiter.username) == username.lower())
            | (func.lower(Recruiter.email) == email)
        ).first()

        if existing_recruiter:
            flash("Username or email already exists.", "danger")
            return redirect(url_for("register"))

        password_hash = generate_password_hash(password)

        recruiter = Recruiter(
            username=username,
            email=email,
            password_hash=password_hash
        )

        try:
            db.session.add(recruiter)
            db.session.commit()

            flash(
                "Registration successful. Please log in.",
                "success"
            )

            return redirect(url_for("login"))

        except IntegrityError:
            db.session.rollback()
            flash("Username or email already exists.", "danger")

        except Exception:
            db.session.rollback()
            app.logger.exception("Recruiter registration failed.")
            flash("Registration failed. Please try again.", "danger")

    return render_template("register.html")


# --------------------------------------------------
# RECRUITER LOGIN
# --------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash(
                "Please enter your username and password.",
                "danger"
            )
            return redirect(url_for("login"))

        recruiter = Recruiter.query.filter(
            func.lower(Recruiter.username) == username.lower()
        ).first()

        if recruiter and check_password_hash(
            recruiter.password_hash,
            password
        ):

            session.clear()

            session["recruiter_id"] = recruiter.id
            session["username"] = recruiter.username

            flash("Login successful.", "success")

            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "danger")

    return render_template("login.html")


# --------------------------------------------------
# CREATE JOB
# --------------------------------------------------

@app.route("/create_job", methods=["GET", "POST"])
def create_job():

    recruiter = get_logged_in_recruiter()

    if not recruiter:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))

    if request.method == "POST":

        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        location = request.form.get("location", "").strip()
        employment_type = request.form.get("employment_type", "").strip()
        education = request.form.get("education", "").strip()

        min_experience = request.form.get(
            "min_experience_years", "0"
        )

        required_skills = request.form.get("required_skills", "")
        preferred_skills = request.form.get("preferred_skills", "")

        if not title or not description:
            flash("Job title and description are required.", "danger")
            return redirect(url_for("create_job"))

        try:
            min_experience = float(min_experience)

            if min_experience < 0:
                raise ValueError

        except ValueError:
            flash("Enter a valid experience requirement.", "danger")
            return redirect(url_for("create_job"))

        try:
            job = Job(
                recruiter_id=recruiter.id,
                title=title,
                description=description,
                location=location,
                employment_type=employment_type,
                min_experience_years=min_experience,
                education=education,
                status="Active"
            )

            db.session.add(job)
            db.session.flush()

            required_skill_names = {
                skill.strip()
                for skill in required_skills.split(",")
                if skill.strip()
            }

            preferred_skill_names = {
                skill.strip()
                for skill in preferred_skills.split(",")
                if skill.strip()
            }

            all_skills = {}

            for skill_name in required_skill_names:
                all_skills[skill_name.lower()] = (
                    skill_name, True
                )

            for skill_name in preferred_skill_names:
                if skill_name.lower() not in all_skills:
                    all_skills[skill_name.lower()] = (
                        skill_name, False
                    )

            for skill_name, is_required in all_skills.values():

                skill = get_or_create_skill(skill_name)

                if skill:
                    job_skill = JobSkill(
                        job_id=job.id,
                        skill_id=skill.id,
                        is_required=is_required
                    )

                    db.session.add(job_skill)

            db.session.commit()

            flash("Job created successfully.", "success")

            return redirect(url_for("jobs"))

        except IntegrityError:
            db.session.rollback()
            flash(
                "Unable to create job due to a database conflict.",
                "danger"
            )

        except Exception:
            db.session.rollback()
            app.logger.exception("Job creation failed.")
            flash("Unable to create job. Please try again.", "danger")

    return render_template("create_job.html")


# --------------------------------------------------
# VIEW ALL JOBS
# --------------------------------------------------

@app.route("/jobs")
def jobs():

    recruiter = get_logged_in_recruiter()

    if not recruiter:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))

    recruiter_jobs = Job.query.filter_by(
        recruiter_id=recruiter.id
    ).order_by(
        Job.created_at.desc()
    ).all()

    return render_template(
        "jobs.html",
        jobs=recruiter_jobs
    )


# --------------------------------------------------
# JOB DETAILS
# --------------------------------------------------

@app.route("/job/<int:job_id>")
def job_details(job_id):

    recruiter = get_logged_in_recruiter()

    if not recruiter:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))

    job = Job.query.filter_by(
        id=job_id,
        recruiter_id=recruiter.id
    ).first_or_404()

    job_skills = db.session.query(
        Skill.skill_name,
        JobSkill.is_required
    ).join(
        JobSkill,
        JobSkill.skill_id == Skill.id
    ).filter(
        JobSkill.job_id == job.id
    ).all()

    return render_template(
        "job_details.html",
        job=job,
        job_skills=job_skills
    )
@app.route("/job/<int:job_id>/delete", methods=["POST"])
def delete_job(job_id):

    recruiter = get_logged_in_recruiter()

    if not recruiter:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))

    # Verify job ownership
    job = Job.query.filter_by(
        id=job_id,
        recruiter_id=recruiter.id
    ).first_or_404()

    job_id = job.id

    # Collect application IDs and candidate IDs
    application_ids = [
        row[0] for row in db.session.query(
            Application.id
        ).filter_by(job_id=job_id).all()
    ]

    candidate_ids = set(
        row[0] for row in db.session.query(
            Application.candidate_id
        ).filter_by(job_id=job_id).all()
    )

    # Collect uploaded resume file paths
    resume_paths = []

    if application_ids:

        resumes = Resume.query.filter(
            Resume.application_id.in_(application_ids)
        ).all()

        resume_paths.extend(
            resume.file_path
            for resume in resumes
            if resume.file_path
        )

    try:

        if application_ids:

            # 1. Find associated analysis IDs
            analysis_ids = [
                row[0] for row in db.session.query(
                    ResumeAnalysis.id
                ).filter(
                    ResumeAnalysis.application_id.in_(application_ids)
                ).all()
            ]

            # 2. Delete Gemini feedback
            if analysis_ids:
                Feedback.query.filter(
                    Feedback.analysis_id.in_(analysis_ids)
                ).delete(synchronize_session=False)

            # 3. Delete resume analyses
            ResumeAnalysis.query.filter(
                ResumeAnalysis.application_id.in_(application_ids)
            ).delete(synchronize_session=False)

            # 4. Delete application-specific resumes
            Resume.query.filter(
                Resume.application_id.in_(application_ids)
            ).delete(synchronize_session=False)

            # 5. Delete applications belonging to this job
            Application.query.filter(
                Application.id.in_(application_ids)
            ).delete(synchronize_session=False)

        # 6. Clean up candidates who have no remaining applications
        for candidate_id in candidate_ids:

            remaining_applications = Application.query.filter_by(
                candidate_id=candidate_id
            ).count()

            if remaining_applications == 0:

                remaining_resumes = Resume.query.filter_by(
                    candidate_id=candidate_id
                ).all()

                for resume in remaining_resumes:
                    if resume.file_path:
                        resume_paths.append(resume.file_path)

                Resume.query.filter_by(
                    candidate_id=candidate_id
                ).delete(synchronize_session=False)

                CandidateSkill.query.filter_by(
                    candidate_id=candidate_id
                ).delete(synchronize_session=False)

                Candidate.query.filter_by(
                    id=candidate_id
                ).delete(synchronize_session=False)

        # 7. Delete job skill mappings
        JobSkill.query.filter_by(
            job_id=job_id
        ).delete(synchronize_session=False)

        # 8. Delete the job
        Job.query.filter_by(
            id=job_id
        ).delete(synchronize_session=False)

        # 9. Commit database changes
        db.session.commit()

        # 10. Delete physical resume files
        for file_path in set(resume_paths):

            try:
                if file_path and os.path.isfile(file_path):
                    os.remove(file_path)

            except OSError:
                app.logger.exception(
                    "Could not delete resume file: %s",
                    file_path
                )

        flash(
            "Job and its associated recruitment records deleted successfully.",
            "success"
        )

    except Exception:

        db.session.rollback()

        app.logger.exception(
            "Job deletion failed."
        )

        flash(
            "Unable to delete job. Please try again.",
            "danger"
        )

    return redirect(url_for("jobs"))

# --------------------------------------------------
# VIEW JOB APPLICANTS
# --------------------------------------------------
@app.route("/job/<int:job_id>/applicants")
def view_applicants(job_id):

    recruiter = get_logged_in_recruiter()

    if not recruiter:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))

    job = Job.query.filter_by(
        id=job_id,
        recruiter_id=recruiter.id
    ).first_or_404()

    applications = Application.query.filter_by(
        job_id=job.id
    ).all()

    results = []

    for application in applications:

        candidate = db.session.get(
            Candidate,
            application.candidate_id
        )

        if not candidate:
            continue

        resume = Resume.query.filter_by(
            application_id=application.id
        ).order_by(
            Resume.uploaded_at.desc()
        ).first()

        analysis = ResumeAnalysis.query.filter_by(
            application_id=application.id
        ).order_by(
            ResumeAnalysis.analysis_date.desc()
        ).first()

        results.append({
            "candidate": candidate,
            "application": application,
            "resume": resume,
            "analysis": analysis
        })

    results.sort(
        key=lambda item: float(
            item["analysis"].overall_score or 0
        ) if item["analysis"] else 0,
        reverse=True
    )

    total_applicants = len(results)

    shortlisted_count = sum(
        1 for item in results
        if item["application"].status == "Shortlisted"
    )

    pending_count = sum(
        1 for item in results
        if item["application"].status == "Pending"
    )

    rejected_count = sum(
        1 for item in results
        if item["application"].status == "Rejected"
    )

    return render_template(
        "applicants.html",
        job=job,
        results=results,
        total_applicants=total_applicants,
        shortlisted_count=shortlisted_count,
        pending_count=pending_count,
        rejected_count=rejected_count
    )

# --------------------------------------------------
# VIEW CANDIDATE DETAILS
# --------------------------------------------------

@app.route("/application/<int:application_id>")
def candidate_details(application_id):

    recruiter = get_logged_in_recruiter()

    if not recruiter:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))

    application = Application.query.join(
        Job,
        Application.job_id == Job.id
    ).filter(
        Application.id == application_id,
        Job.recruiter_id == recruiter.id
    ).first_or_404()

    candidate = application.candidate

    resume = Resume.query.filter_by(
        application_id=application.id
    ).order_by(
        Resume.uploaded_at.desc()
    ).first()

    analysis = ResumeAnalysis.query.filter_by(
        application_id=application.id
    ).order_by(
        ResumeAnalysis.analysis_date.desc()
    ).first()

    resume_info = {}

    if resume and resume.extracted_text:
        resume_info = extract_resume_information(
            resume.extracted_text
        )

    feedbacks = []

    if analysis:
        feedbacks = analysis.feedback

    return render_template(
        "candidate_details.html",
        application=application,
        candidate=candidate,
        resume=resume,
        analysis=analysis,
        resume_info=resume_info,
        feedbacks=feedbacks
    )

# --------------------------------------------------
# UPDATE CANDIDATE APPLICATION STATUS
# --------------------------------------------------

@app.route("/application/<int:application_id>/status", methods=["POST"])
def update_application_status(application_id):

    recruiter = get_logged_in_recruiter()

    if not recruiter:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))

    application = Application.query.join(
        Job,
        Application.job_id == Job.id
    ).filter(
        Application.id == application_id,
        Job.recruiter_id == recruiter.id
    ).first_or_404()

    new_status = request.form.get("status")

    if new_status not in ["Shortlisted", "Rejected"]:
        flash("Invalid application status.", "danger")
        return redirect(
            url_for("candidate_details", application_id=application.id)
        )

    application.status = new_status

    try:
        db.session.commit()
        flash(
            f"Candidate successfully marked as {new_status}.",
            "success"
        )
    except Exception:
        db.session.rollback()
        flash("Unable to update application status.", "danger")

    return redirect(
        url_for("candidate_details", application_id=application.id)
    )
# --------------------------------------------------
# DELETE CANDIDATE APPLICATION
# --------------------------------------------------
# --------------------------------------------------
# DELETE CANDIDATE APPLICATION
# --------------------------------------------------

@app.route(
    "/application/<int:application_id>/delete",
    methods=["POST"]
)
def delete_application(application_id):

    recruiter = get_logged_in_recruiter()

    if not recruiter:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))

    # Verify application ownership
    application = Application.query.join(
        Job,
        Application.job_id == Job.id
    ).filter(
        Application.id == application_id,
        Job.recruiter_id == recruiter.id
    ).first_or_404()

    # Store IDs before deleting the application
    job_id = application.job_id
    candidate = application.candidate
    candidate_id = candidate.id

    # Collect uploaded resume file paths
    resume_paths = [
        resume.file_path
        for resume in application.resumes
        if resume.file_path
    ]

    try:

        # 1. Delete associated feedback
        analyses = ResumeAnalysis.query.filter_by(
            application_id=application_id
        ).all()

        for analysis in analyses:

            Feedback.query.filter_by(
                analysis_id=analysis.id
            ).delete(synchronize_session=False)

        # 2. Delete resume analysis records
        ResumeAnalysis.query.filter_by(
            application_id=application_id
        ).delete(synchronize_session=False)

        # 3. Delete application-specific resumes
        Resume.query.filter_by(
            application_id=application_id
        ).delete(synchronize_session=False)

        # 4. Delete application directly
        Application.query.filter_by(
            id=application_id
        ).delete(synchronize_session=False)

        db.session.flush()
        # 5. Check for other applications
        remaining_applications = Application.query.filter_by(
            candidate_id=candidate_id
        ).count()

        # 6. Delete candidate only if no applications remain
        if remaining_applications == 0:

            # Delete any remaining candidate resumes
            remaining_resumes = Resume.query.filter_by(
                candidate_id=candidate_id
            ).all()

            for resume in remaining_resumes:

                if resume.file_path:
                    resume_paths.append(resume.file_path)

                db.session.delete(resume)

            # Delete candidate skills
            CandidateSkill.query.filter_by(
                candidate_id=candidate_id
            ).delete(synchronize_session=False)

            # Delete candidate
            db.session.delete(candidate)

        # 7. Commit database changes
        db.session.commit()

        # 8. Delete physical PDF files
        for file_path in set(resume_paths):

            try:
                if file_path and os.path.isfile(file_path):
                    os.remove(file_path)

            except OSError:
                app.logger.exception(
                    "Could not delete resume file: %s",
                    file_path
                )

        flash(
            "Applicant successfully deleted.",
            "success"
        )

    except Exception:

        db.session.rollback()

        app.logger.exception(
            "Applicant deletion failed."
        )

        flash(
            "Unable to delete applicant. Please try again.",
            "danger"
        )

    return redirect(
        url_for("view_applicants", job_id=job_id)
    )
# --------------------------------------------------
# UPLOAD AND SCREEN RESUMES
# --------------------------------------------------

@app.route("/upload_resumes/<int:job_id>", methods=["GET", "POST"])
def upload_resumes(job_id):

    recruiter = get_logged_in_recruiter()

    if not recruiter:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))

    job = Job.query.filter_by(
        id=job_id,
        recruiter_id=recruiter.id
    ).first_or_404()

    if request.method == "POST":

        uploaded_files = request.files.getlist("resumes")

        if not uploaded_files or all(
            not file.filename for file in uploaded_files
        ):
            flash("Please select at least one resume.", "warning")
            return redirect(
                url_for("upload_resumes", job_id=job.id)
            )

        for uploaded_file in uploaded_files:

            if not uploaded_file or not uploaded_file.filename:
                continue

            if not allowed_file(uploaded_file.filename):
                flash(
                    f"{uploaded_file.filename}: Only PDF files are allowed.",
                    "danger"
                )
                continue

            original_filename = secure_filename(
                uploaded_file.filename
            )

            stored_filename = f"{uuid.uuid4().hex}.pdf"

            file_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                stored_filename
            )

            try:
                uploaded_file.stream.seek(0)
                file_header = uploaded_file.stream.read(5)
                uploaded_file.stream.seek(0)

                if file_header != b"%PDF-":
                    flash(
                        f"{original_filename}: Invalid PDF file.",
                        "danger"
                    )
                    continue

                uploaded_file.save(file_path)

                extracted_text = extract_text_from_pdf(file_path)

                resume_info = extract_resume_information(
                    extracted_text
                )

                candidate_name = resume_info.get("name")
                candidate_email = resume_info.get("email")
                candidate_phone = resume_info.get("phone")
                candidate_location = resume_info.get("location")

                candidate_skills = resume_info.get("skills", [])

                if not candidate_name or not candidate_email:

                    os.remove(file_path)

                    flash(
                        f"{original_filename}: Name or email could not be extracted.",
                        "warning"
                    )
                    continue

                candidate_email = candidate_email.strip().lower()

                candidate = Candidate.query.filter(
                    func.lower(Candidate.email) == candidate_email
                ).first()

                if not candidate:

                    candidate = Candidate(
                        name=candidate_name,
                        email=candidate_email,
                        phone=candidate_phone,
                        location=candidate_location
                    )

                    db.session.add(candidate)
                    db.session.flush()

                else:

                    if not candidate.phone and candidate_phone:
                        candidate.phone = candidate_phone

                    if not candidate.location and candidate_location:
                        candidate.location = candidate_location

                    if not candidate.name and candidate_name:
                        candidate.name = candidate_name

                application = Application.query.filter_by(
                    candidate_id=candidate.id,
                    job_id=job.id
                ).first()

                if not application:

                    application = Application(
                        candidate_id=candidate.id,
                        job_id=job.id,
                        status="Pending"
                    )

                    db.session.add(application)
                    db.session.flush()

                # Save candidate skills

                for skill_name in candidate_skills:

                    skill = get_or_create_skill(skill_name)

                    if not skill:
                        continue

                    existing_candidate_skill = CandidateSkill.query.filter_by(
                        candidate_id=candidate.id,
                        skill_id=skill.id
                    ).first()

                    if not existing_candidate_skill:

                        candidate_skill = CandidateSkill(
                            candidate_id=candidate.id,
                            skill_id=skill.id,
                            evidence="Detected in uploaded resume."
                        )

                        db.session.add(candidate_skill)

                # Save resume

                resume = Resume(
                    candidate_id=candidate.id,
                    application_id=application.id,
                    original_filename=original_filename,
                    stored_filename=stored_filename,
                    file_path=file_path,
                    extracted_text=extracted_text
                )

                db.session.add(resume)
                db.session.commit()

                flash(
                    f"{original_filename}: Resume uploaded successfully.",
                    "success"
                )

            except ValueError as error:

                db.session.rollback()

                if os.path.exists(file_path):
                    os.remove(file_path)

                flash(
                    f"{original_filename}: {str(error)}",
                    "danger"
                )

            except Exception:

                db.session.rollback()

                if os.path.exists(file_path):
                    os.remove(file_path)

                app.logger.exception(
                    "Resume processing failed for %s",
                    original_filename
                )

                flash(
                    f"{original_filename}: Unable to process resume.",
                    "danger"
                )

        # --------------------------------------------------
        # SCREEN APPLICATIONS FOR THIS JOB
        # --------------------------------------------------

        applications = Application.query.filter_by(
            job_id=job.id
        ).all()

        job_skills = db.session.query(
            Skill.skill_name,
            JobSkill.is_required
        ).join(
            JobSkill,
            JobSkill.skill_id == Skill.id
        ).filter(
            JobSkill.job_id == job.id
        ).all()

        results = []

        for application in applications:

            candidate = db.session.get(
                Candidate,
                application.candidate_id
            )

            if not candidate:
                continue

            latest_resume = Resume.query.filter_by(
                application_id=application.id
            ).order_by(
                Resume.uploaded_at.desc()
            ).first()

            if not latest_resume:
                continue

            resume_info = extract_resume_information(
                latest_resume.extracted_text
            )

            candidate_skill_names = resume_info.get(
                "skills", []
            )

            # 1. Skill matching

            skill_result = calculate_skill_match(
                candidate_skill_names,
                job_skills
            )

            skill_match_score = skill_result[
                "skill_match_score"
            ]

            # Required skills

            required_skills = [
                skill
                for skill, is_required in job_skills
                if is_required
            ]

            # Preferred skills

            preferred_skills = [
                skill
                for skill, is_required in job_skills
                if not is_required
            ]

            # 2. TF-IDF similarity

            tfidf_score = calculate_tfidf_similarity(
                latest_resume.extracted_text,
                job.description
            )

            # 3. Semantic similarity

            semantic_score = calculate_semantic_similarity(
                latest_resume.extracted_text,
                job.description
            )

            # 4. Overall score

            overall_score = calculate_overall_score(
                skill_match_score,
                tfidf_score,
                semantic_score
            )

            # Find existing analysis

            analysis = ResumeAnalysis.query.filter_by(
                application_id=application.id
            ).first()

            if analysis:

                analysis.skill_match_score = skill_match_score
                analysis.tfidf_score = tfidf_score
                analysis.semantic_score = semantic_score
                analysis.overall_score = overall_score

                analysis.model_version = (
                    "TF-IDF + all-MiniLM-L6-v2"
                )

            else:

                analysis = ResumeAnalysis(
                    application_id=application.id,
                    skill_match_score=skill_match_score,
                    tfidf_score=tfidf_score,
                    semantic_score=semantic_score,
                    overall_score=overall_score,
                    model_version="TF-IDF + all-MiniLM-L6-v2"
                )

                db.session.add(analysis)

                    # 1. Ensure analysis has a database ID
            db.session.flush()

            # 2. Generate Gemini AI feedback
            feedback_result = generate_resume_feedback(
                resume_text=latest_resume.extracted_text,
                job_title=job.title,
                job_description=job.description,
                required_skills=required_skills,
                preferred_skills=preferred_skills,
                skill_match_score=skill_match_score,
                tfidf_score=tfidf_score,
                semantic_score=semantic_score,
                overall_score=overall_score
            )

            # 3. Check whether feedback already exists
            existing_feedback = Feedback.query.filter_by(
                analysis_id=analysis.id
            ).first()

            # 4. Update existing feedback or create new feedback
            if existing_feedback:

                existing_feedback.feedback_text = (
                    feedback_result["feedback_text"]
                )

                existing_feedback.generated_by = (
                    feedback_result["generated_by"]
                )

            else:

                new_feedback = Feedback(
                    analysis_id=analysis.id,
                    feedback_text=feedback_result["feedback_text"],
                    generated_by=feedback_result["generated_by"]
                )

                db.session.add(new_feedback)

            # 5. Add candidate results
            results.append({
                "candidate": candidate,
                "application": application,
                "resume": latest_resume,

                "matching": skill_result,
                "skill_result": skill_result,

                "skill_match_score": skill_match_score,
                "tfidf_score": tfidf_score,
                "semantic_score": semantic_score,
                "overall_score": overall_score,

                "feedback": feedback_result["feedback_text"],
                "generated_by": feedback_result["generated_by"]
            })
        db.session.commit()

        results.sort(
            key=lambda item: item["overall_score"],
            reverse=True
        )

        return render_template(
            "upload_resumes.html",
            job=job,
            results=results,
            application_results=results
        )

    return render_template(
        "upload_resumes.html",
        job=job,
        results=[],
        application_results=[]
    )

# --------------------------------------------------
# RECRUITER DASHBOARD
# --------------------------------------------------

@app.route("/dashboard")
def dashboard():

    recruiter = get_logged_in_recruiter()

    if not recruiter:
        flash("Please log in first.", "warning")
        return redirect(url_for("login"))

    total_jobs = Job.query.filter_by(
        recruiter_id=recruiter.id
    ).count()

    active_jobs = Job.query.filter_by(
        recruiter_id=recruiter.id,
        status="Active"
    ).count()

    applications = db.session.query(
        Application
    ).join(
        Job,
        Application.job_id == Job.id
    ).filter(
        Job.recruiter_id == recruiter.id
    ).all()

    total_applications = len(applications)

    shortlisted = sum(
        1 for application in applications
        if application.status == "Shortlisted"
    )

    rejected = sum(
        1 for application in applications
        if application.status == "Rejected"
    )

    pending = sum(
        1 for application in applications
        if application.status == "Pending"
    )

    total_candidates = db.session.query(
        func.count(func.distinct(Application.candidate_id))
    ).join(
        Job,
        Application.job_id == Job.id
    ).filter(
        Job.recruiter_id == recruiter.id
    ).scalar() or 0

    average_score = db.session.query(
        func.avg(ResumeAnalysis.overall_score)
    ).join(
        Application,
        ResumeAnalysis.application_id == Application.id
    ).join(
        Job,
        Application.job_id == Job.id
    ).filter(
        Job.recruiter_id == recruiter.id
    ).scalar()

    average_score = (
        round(float(average_score), 2)
        if average_score else 0
    )

    return render_template(
        "dashboard.html",
        recruiter=recruiter,
        total_jobs=total_jobs,
        active_jobs=active_jobs,
        total_applications=total_applications,
        total_candidates=total_candidates,
        shortlisted=shortlisted,
        rejected=rejected,
        pending=pending,
        average_score=average_score
    )


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

@app.route("/logout")
def logout():

    session.clear()

    flash("You have been logged out.", "success")

    return redirect(url_for("login"))


# --------------------------------------------------
# FILE SIZE ERROR HANDLER
# --------------------------------------------------

@app.errorhandler(413)
def file_too_large(error):

    flash(
        "The uploaded file is too large. Maximum allowed size is 10 MB.",
        "danger"
    )

    return redirect(
        request.referrer or url_for("dashboard")
    )


# --------------------------------------------------
# APPLICATION ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
