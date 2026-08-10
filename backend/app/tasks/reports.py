# 9 aug 26 · html + mail 10 aug 26
# Christiano Fernandes
# reports.py
# monthly placement report for the admin
#
# Runs at 07:00 on the 1st (see beat_schedule in config.py) and summarises the
# month that just ended. The Admin model exists to give this job a recipient.
#
# The report is rendered from a Jinja2 template rather than assembled as a
# string: it is a document, it has a table, and the same template is what a
# mail client receives. Jinja2 also escapes the company names for free.


from datetime import date, datetime, timedelta

from celery import shared_task
from flask import render_template

from app.extensions import db
from app.models import (
    Admin,
    Application,
    ApplicationStatus,
    Company,
    Drive,
    Placement,
    Role,
    User,
)
from app.tasks.notify import notify


def _previous_month(today):
    """First and last day of the month before `today`."""
    last_of_prev = today.replace(day=1) - timedelta(days=1)
    return last_of_prev.replace(day=1), last_of_prev


@shared_task(name="reports.monthly_placement_report")
def monthly_placement_report():
    start, end = _previous_month(date.today())
    first, last = start.isoformat(), end.isoformat()

    def applications_where(date_column, *filters):
        return (
            db.session.query(db.func.count(Application.id))
            .filter(
                db.func.date(date_column) >= first,
                db.func.date(date_column) <= last,
                *filters,
            )
            .scalar()
            or 0
        )

    # statusUpdatedAt holds only the LAST change, so these count applications
    # that ENDED the month in each state — not every transition through it.
    def ended_as(status):
        return applications_where(Application.statusUpdatedAt, Application.status == status)

    # Placements are the exception, and the only exact figure here: placedAt is
    # written once when the student accepts and never rewritten.
    placed = (
        db.session.query(db.func.count(Placement.id))
        .filter(db.func.date(Placement.placedAt) >= first, db.func.date(Placement.placedAt) <= last)
        .scalar()
        or 0
    )

    stats = {
        "newApplications": applications_where(Application.appliedAt),
        "offers": ended_as(ApplicationStatus.OFFER) + placed,
        "placed": placed,
        "rejected": ended_as(ApplicationStatus.REJECTED),
        "declined": ended_as(ApplicationStatus.DECLINED),
        "drivesPosted": (
            db.session.query(db.func.count(Drive.id))
            .filter(db.func.date(Drive.createdAt) >= first, db.func.date(Drive.createdAt) <= last)
            .scalar()
            or 0
        ),
    }

    # One join instead of two: the register carries companyId directly, so this
    # no longer has to route through Drive to find out who placed whom.
    companies = (
        db.session.query(Company.name, db.func.count(Placement.id))
        .join(Placement, Placement.companyId == Company.id)
        .filter(
            db.func.date(Placement.placedAt) >= first,
            db.func.date(Placement.placedAt) <= last,
        )
        .group_by(Company.name)
        .order_by(db.func.count(Placement.id).desc())
        .all()
    )

    month = start.strftime("%B %Y")
    html = render_template(
        "monthly_report.html",
        month=month,
        start=start,
        end=end,
        stats=stats,
        companies=companies,
        generatedAt=datetime.now(),
    )

    # The bell gets the summary line; the mailbox gets the rendered document.
    summary = (
        f"{stats['newApplications']} new applications, {stats['offers']} offers, "
        f"{stats['placed']} placed."
    )

    admins = (
        db.session.query(User.id, Admin.email)
        .join(Admin, Admin.userId == User.id)
        .filter(User.role == Role.ADMIN)
        .all()
    )

    for user_id, email in admins:
        notify(user_id, f"Placement report — {month}", summary, email=email, html=html)

    db.session.commit()
    return {"month": start.strftime("%Y-%m"), "placed": stats["placed"], "admins": len(admins)}
