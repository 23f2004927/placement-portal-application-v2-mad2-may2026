# 10 aug 26
# Christiano Fernandes
# resumes.py
# /api/student/resume and /api/students/<id>/resume
#
# Its own blueprint rather than part of profile.py: the profile endpoints are
# JSON, this one is multipart, and mixing them would make that route branch on
# content type.
#
# The files live on disk under instance/uploads/resumes/, not in SQLite. The
# "SQLite only" constraint is about the database; storing PDFs as BLOBs would
# make every student query drag megabytes along with it.


import os
from datetime import datetime

from flask import Blueprint, current_app, jsonify, request, send_from_directory

from app.extensions import db
from app.models import Application, Drive, Student
from app.policies import HIDDEN_FROM_COMPANY
from app.utils.caching import invalidate
from app.utils.decorators import role_required
from app.utils.identity import current_company, current_role, current_student

resumes_bp = Blueprint("resumes", __name__, url_prefix="/api")

MAX_MB = 2
PDF_MAGIC = b"%PDF-"


def resume_dir():
    path = os.path.join(current_app.instance_path, "uploads", "resumes")
    os.makedirs(path, exist_ok=True)
    return path


def stored_name(student_id):
    """Derived from the id, so the client's filename is never trusted, never
    stored, and never used to build a path. That also makes re-upload an
    overwrite, which is exactly what "update my resume" should do."""
    return f"student_{student_id}.pdf"


def _may_read(student_id):
    """Who may read this student's resume.

    This belongs with the other rules in policies.py, but that module promises
    to stay Flask-free and query-free and the company case needs a join: a
    company may read a resume only if the student has applied to one of ITS
    drives. Without that check any logged-in company could walk the id range
    and collect every resume in the portal.
    """
    role = current_role()

    if role == "admin":
        return True

    if role == "student":
        student = current_student()
        return student is not None and student.id == student_id

    if role == "company":
        company = current_company()
        if company is None:
            return False
        # notin_(HIDDEN_FROM_COMPANY) keeps this consistent with the list: a
        # revoked application is invisible there, so it must not be a way in.
        return db.session.query(
            Application.query.join(Application.drive)
            .filter(
                Drive.companyId == company.id,
                Application.studentId == student_id,
                Application.status.notin_(HIDDEN_FROM_COMPANY),
            )
            .exists()
        ).scalar()

    return False


@resumes_bp.route("/student/resume", methods=["POST"])
@role_required("student")
def upload_resume():
    student = current_student()
    if student is None:
        return jsonify(message="No student profile for this account."), 403

    file = request.files.get("file")
    if file is None or not file.filename:
        return jsonify(message="Choose a PDF to upload."), 400

    if not file.filename.lower().endswith(".pdf"):
        return jsonify(message="Resumes must be a PDF."), 400

    # An extension proves nothing — anything can be renamed .pdf. A real PDF
    # opens with %PDF-. Seek back afterwards or the saved file loses 5 bytes.
    head = file.stream.read(len(PDF_MAGIC))
    file.stream.seek(0)
    if head != PDF_MAGIC:
        return jsonify(message="That file is not a valid PDF."), 400

    file.save(os.path.join(resume_dir(), stored_name(student.id)))

    student.resume = stored_name(student.id)
    student.resumeUploadedAt = datetime.now()
    db.session.commit()
    invalidate("students")

    return jsonify(resumeUploadedAt=student.resumeUploadedAt.isoformat()), 200


@resumes_bp.route("/student/resume", methods=["DELETE"])
@role_required("student")
def delete_resume():
    student = current_student()
    if student is None:
        return jsonify(message="No student profile for this account."), 403

    if student.resume:
        path = os.path.join(resume_dir(), student.resume)
        # Guarded: a file removed by hand shouldn't leave the row unclearable.
        if os.path.exists(path):
            os.remove(path)

    student.resume = None
    student.resumeUploadedAt = None
    db.session.commit()
    invalidate("students")

    return jsonify(resumeUploadedAt=None), 200


@resumes_bp.route("/students/<int:student_id>/resume", methods=["GET"])
@role_required("student", "company", "admin")
def read_resume(student_id):
    if not _may_read(student_id):
        return jsonify(message="Forbidden"), 403

    student = db.session.get(Student, student_id)
    if student is None or not student.resume:
        return jsonify(message="No resume on file."), 404

    if not os.path.exists(os.path.join(resume_dir(), student.resume)):
        return jsonify(message="No resume on file."), 404

    # Inline, not an attachment: a recruiter screening a stack wants it to open
    # in the browser's viewer rather than pile up in Downloads.
    return send_from_directory(
        resume_dir(),
        student.resume,
        mimetype="application/pdf",
        as_attachment=False,
        download_name=f"{student.name} - Resume.pdf",
    )
