# 9 aug 26
# Christiano Fernandes
# exports.py
# user-triggered CSV export of a student's placement history
#
# Asynchronous by requirement. The request returns a task id immediately; the
# worker writes a file into instance/exports/ and the browser polls for it.


import csv
import os

from celery import shared_task
from flask import current_app

from app.models import Application, Student
from app.tasks.notify import notify

COLUMNS = [
    "Company",
    "Role",
    "Applied on",
    "Status",
    "Interview",
    "Feedback",
    "Offer letter issued",
]


def export_dir():
    path = os.path.join(current_app.instance_path, "exports")
    os.makedirs(path, exist_ok=True)
    return path


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
    path = os.path.join(export_dir(), filename)

    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(COLUMNS)
        for a in applications:
            writer.writerow(
                [
                    a.drive.company.name,
                    a.drive.title,
                    a.appliedAt.strftime("%Y-%m-%d") if a.appliedAt else "",
                    a.status.value,
                    a.interviewScheduledAt.strftime("%Y-%m-%d %H:%M")
                    if a.interviewScheduledAt
                    else "",
                    a.feedback or "",
                    "yes" if a.offerLetter else "no",
                ]
            )

    notify(
        user_id,
        "Your export is ready",
        f"{len(applications)} applications exported to CSV.",
    )
    from app.extensions import db

    db.session.commit()

    # userId is returned so the download route can prove ownership without a
    # second table: the result backend already holds it.
    return {"userId": user_id, "rows": len(applications), "filename": filename}
