# 9 aug 26
# Christiano Fernandes
# reminders.py
# daily scheduled reminder for students
#
# Runs at 09:00 IST (see beat_schedule in config.py). Two reminders, both
# written as in-app notifications:
#   1. an interview happening tomorrow
#   2. a drive the student is eligible for whose deadline is close


from datetime import date, datetime, timedelta

from celery import shared_task

from app.extensions import db
from app.models import Application, ApplicationStatus, Drive, DriveStatus
from app.tasks.notify import notify

# How far ahead a closing deadline counts as "closing soon".
DEADLINE_WINDOW_DAYS = 3


@shared_task(name="reminders.daily_student_reminders")
def daily_student_reminders():
    tomorrow = date.today() + timedelta(days=1)
    sent = 0

    # 1. Interviews tomorrow.
    #    db.func.date() strips the time part in SQL — comparing a DateTime
    #    column straight to a date would only ever match exactly midnight.
    interviews = (
        Application.query.filter(
            Application.status == ApplicationStatus.INTERVIEW,
            db.func.date(Application.interviewScheduledAt) == tomorrow.isoformat(),
        ).all()
    )

    for application in interviews:
        notify(
            application.student.userId,
            "Interview tomorrow",
            f"{application.drive.company.name} — {application.drive.title} "
            f"at {application.interviewScheduledAt.strftime('%H:%M')}.",
        )
        sent += 1

    # 2. Drives closing soon that the student has not applied to.
    closing = Drive.query.filter(
        Drive.status == DriveStatus.APPROVED,
        Drive.applicationDeadline.isnot(None),
        Drive.applicationDeadline >= datetime.now(),
        Drive.applicationDeadline <= datetime.now() + timedelta(days=DEADLINE_WINDOW_DAYS),
    ).all()

    if closing:
        # One query for every application, rather than one per student per drive.
        applied = {
            (row[0], row[1])
            for row in db.session.query(Application.studentId, Application.driveId).all()
        }

        for drive in closing:
            for student in _eligible_students(drive):
                if (student.id, drive.id) in applied:
                    continue
                notify(
                    student.userId,
                    "Drive closing soon",
                    f"{drive.company.name} — {drive.title} closes on "
                    f"{drive.applicationDeadline.strftime('%d %b')}.",
                )
                sent += 1

    db.session.commit()
    return {"notifications": sent}


def _eligible_students(drive):
    """Same NULL-means-no-restriction rules the student drive list uses."""
    from app.models import Student

    query = Student.query
    if drive.branch is not None:
        query = query.filter(Student.branch == drive.branch)
    if drive.minCgpa is not None:
        query = query.filter(Student.cgpa >= drive.minCgpa)
    if drive.eligibleYear is not None:
        query = query.filter(Student.gradeYear == drive.eligibleYear)
    return query.all()
