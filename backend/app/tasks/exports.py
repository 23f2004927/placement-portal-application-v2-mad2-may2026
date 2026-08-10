# 9 aug 26 · company export 10 aug 26
# Christiano Fernandes
# exports.py
# user-triggered CSV exports
#
# Asynchronous by requirement. The request returns a task id immediately; the
# worker writes a file into instance/exports/ and the browser polls for it.
#
# Two tasks, one per role, rather than one task branching on who asked: the
# columns differ, and a student's export must never be able to widen into a
# company's by passing the wrong id. Both return userId, so the download route
# proves ownership the same way for either.


import csv
import os

from celery import shared_task
from flask import current_app

from app.extensions import db
from app.models import Application, Company, Drive, Student
from app.tasks.notify import notify

STUDENT_COLUMNS = [
    "Student ID",
    "Company",
    "Role",
    "Applied on",
    "Status",
    "Last updated",
    "Interview",
    "Feedback",
    "Offer letter issued",
]

COMPANY_COLUMNS = [
    "Student ID",
    "Candidate",
    "Branch",
    "CGPA",
    "Drive",
    "Applied on",
    "Status",
    "Last updated",
    "Interview",
    "Feedback",
]


def export_dir():
    path = os.path.join(current_app.instance_path, "exports")
    os.makedirs(path, exist_ok=True)
    return path


def _date(value, fmt="%Y-%m-%d"):
    return value.strftime(fmt) if value else ""


def _write(filename, columns, rows):
    with open(os.path.join(export_dir(), filename), "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        writer.writerows(rows)


@shared_task(bind=True, name="exports.student_applications_csv")
def student_applications_csv(self, user_id):
    """bind=True gives us `self`, and self.request.id is the task id — which is
    also the filename, so the download route can find the file from the id
    alone with nothing else to store."""
    student = Student.query.filter_by(userId=user_id).first()
    if student is None:
        return {"error": "No student profile for this account."}

    applications = (
        Application.query.filter_by(studentId=student.id)
        .order_by(Application.appliedAt.desc())
        .all()
    )

    filename = f"{self.request.id}.csv"
    _write(
        filename,
        STUDENT_COLUMNS,
        [
            [
                student.rollNumber,
                a.drive.company.name,
                a.drive.title,
                _date(a.appliedAt),
                a.status.value,
                _date(a.statusUpdatedAt),
                _date(a.interviewScheduledAt, "%Y-%m-%d %H:%M"),
                a.feedback or "",
                "yes" if a.offerLetter else "no",
            ]
            for a in applications
        ],
    )

    notify(
        user_id,
        "Your export is ready",
        f"{len(applications)} applications exported to CSV.",
        email=student.email,
    )
    db.session.commit()

    # userId is returned so the download route can prove ownership without a
    # second table: the result backend already holds it.
    return {"userId": user_id, "rows": len(applications), "filename": filename}


@shared_task(bind=True, name="exports.company_applications_csv")
def company_applications_csv(self, user_id):
    """Every applicant across this company's drives — its side of the same
    record the student exports."""
    company = Company.query.filter_by(userId=user_id).first()
    if company is None:
        return {"error": "No company profile for this account."}

    applications = (
        Application.query.join(Application.drive)
        .filter(Drive.companyId == company.id)
        .order_by(Application.appliedAt.desc())
        .all()
    )

    filename = f"{self.request.id}.csv"
    _write(
        filename,
        COMPANY_COLUMNS,
        [
            [
                a.student.rollNumber,
                a.student.name,
                a.student.branch.value if a.student.branch else "",
                a.student.cgpa,
                a.drive.title,
                _date(a.appliedAt),
                a.status.value,
                _date(a.statusUpdatedAt),
                _date(a.interviewScheduledAt, "%Y-%m-%d %H:%M"),
                a.feedback or "",
            ]
            for a in applications
        ],
    )

    notify(
        user_id,
        "Your export is ready",
        f"{len(applications)} applications exported to CSV.",
        email=company.hrContactEmail,
    )
    db.session.commit()

    return {"userId": user_id, "rows": len(applications), "filename": filename}
