# 9 aug 26
# Christiano Fernandes
# reports.py
# monthly placement report for the admin
#
# Runs at 07:00 on the 1st (see beat_schedule in config.py) and summarises the
# month that just ended. The Admin model exists to give this job a recipient.


from datetime import date, timedelta

from celery import shared_task

from app.extensions import db
from app.models import Application, ApplicationStatus, Role, User
from app.tasks.notify import notify


def _previous_month(today):
    """First and last day of the month before `today`."""
    last_of_prev = today.replace(day=1) - timedelta(days=1)
    return last_of_prev.replace(day=1), last_of_prev


@shared_task(name="reports.monthly_placement_report")
def monthly_placement_report():
    start, end = _previous_month(date.today())

    def count(*filters):
        return (
            db.session.query(db.func.count(Application.id))
            .filter(
                db.func.date(Application.statusUpdatedAt) >= start.isoformat(),
                db.func.date(Application.statusUpdatedAt) <= end.isoformat(),
                *filters,
            )
            .scalar()
            or 0
        )

    placed = count(Application.status == ApplicationStatus.PLACED)
    offers = count(Application.status == ApplicationStatus.OFFER)
    rejected = count(Application.status == ApplicationStatus.REJECTED)

    new_applications = (
        db.session.query(db.func.count(Application.id))
        .filter(
            db.func.date(Application.appliedAt) >= start.isoformat(),
            db.func.date(Application.appliedAt) <= end.isoformat(),
        )
        .scalar()
        or 0
    )

    body = (
        f"{new_applications} new applications. "
        f"{offers} offers made, {placed} students placed, {rejected} rejected."
    )

    admins = User.query.filter_by(role=Role.ADMIN).all()
    for admin in admins:
        notify(admin.id, f"Placement report — {start.strftime('%B %Y')}", body)

    db.session.commit()
    return {"month": start.strftime("%Y-%m"), "placed": placed, "admins": len(admins)}
