# 7 aug 26
# Christiano Fernandes
# stats.py
# dashboard counts, one endpoint per role
#
# Split by role rather than shared, because unlike /api/applications these are
# not the same resource filtered three ways — they are three different questions.
# Counting happens in SQL (func.count) rather than len(query.all()), so no rows
# cross the wire to be discarded.


from datetime import datetime, timedelta

from flask import Blueprint, jsonify
from sqlalchemy import func

from app.extensions import db
from app.models import (
    AccountStatus,
    Application,
    ApplicationStatus,
    Company,
    Drive,
    DriveStatus,
    Student,
    User,
)
from app.utils.decorators import role_required
from app.utils.identity import current_company, current_student

stats_bp = Blueprint("stats", __name__, url_prefix="/api")


def _count(model, *filters):
    query = db.session.query(func.count(model.id))
    if filters:
        query = query.filter(*filters)
    return query.scalar() or 0


@stats_bp.route("/student/stats", methods=["GET"])
@role_required("student")
def student_stats():
    student = current_student()
    if student is None:
        return jsonify(message="No student profile for this account."), 403

    mine = Application.studentId == student.id

    return jsonify(
        openDrives=_count(Drive, Drive.status == DriveStatus.APPROVED),
        applications=_count(Application, mine, Application.status != ApplicationStatus.REVOKED),
        shortlisted=_count(Application, mine, Application.status == ApplicationStatus.SHORTLISTED),
        interviews=_count(Application, mine, Application.status == ApplicationStatus.INTERVIEW),
        offers=_count(Application, mine, Application.status == ApplicationStatus.OFFER),
        placed=_count(Application, mine, Application.status == ApplicationStatus.PLACED),
    ), 200


@stats_bp.route("/company/stats", methods=["GET"])
@role_required("company")
def company_stats():
    company = current_company()
    if company is None:
        return jsonify(message="No company profile for this account."), 403

    # Applications reach a company only through its drives, so every count here
    # joins rather than filtering Application directly.
    def applications_where(*extra):
        return (
            db.session.query(func.count(Application.id))
            .join(Drive, Application.driveId == Drive.id)
            .filter(
                Drive.companyId == company.id,
                Application.status != ApplicationStatus.REVOKED,
                *extra,
            )
            .scalar()
            or 0
        )

    week_ahead = datetime.now() + timedelta(days=7)

    return jsonify(
        drives=_count(Drive, Drive.companyId == company.id),
        openDrives=_count(
            Drive, Drive.companyId == company.id, Drive.status == DriveStatus.APPROVED
        ),
        applications=applications_where(),
        shortlisted=applications_where(Application.status == ApplicationStatus.SHORTLISTED),
        offers=applications_where(Application.status == ApplicationStatus.OFFER),
        placed=applications_where(Application.status == ApplicationStatus.PLACED),
        # --- queues: what needs attention now, same live-not-cached rule as admin
        toReview=applications_where(Application.status == ApplicationStatus.APPLIED),
        interviewsThisWeek=applications_where(
            Application.status == ApplicationStatus.INTERVIEW,
            Application.interviewScheduledAt.isnot(None),
            Application.interviewScheduledAt >= datetime.now(),
            Application.interviewScheduledAt <= week_ahead,
        ),
        offersAwaiting=applications_where(Application.status == ApplicationStatus.OFFER),
        drivesPending=_count(
            Drive, Drive.companyId == company.id, Drive.status == DriveStatus.PENDING
        ),
    ), 200


@stats_bp.route("/admin/stats", methods=["GET"])
@role_required("admin")
def admin_stats():
    """Deliberately NOT cached, unlike /api/admin/analytics.

    The queue counts below are work an admin is about to act on: approve a
    company and the number must drop on the next load. A cached queue is worse
    than no queue, because it invites them to click something that has already
    moved.
    """
    week_ahead = datetime.now() + timedelta(days=7)

    return jsonify(
        students=_count(Student),
        companies=_count(Company),
        drives=_count(Drive),
        applications=_count(Application, Application.status != ApplicationStatus.REVOKED),
        placed=_count(Application, Application.status == ApplicationStatus.PLACED),
        # --- queues: what needs attention now -------------------------------
        # Split from the old combined pendingApprovals so each tile can link to
        # the list that resolves it.
        pendingCompanies=_count(User, User.accountStatus == AccountStatus.PENDING),
        pendingDrives=_count(Drive, Drive.status == DriveStatus.PENDING),
        offersAwaiting=_count(Application, Application.status == ApplicationStatus.OFFER),
        interviewsThisWeek=_count(
            Application,
            Application.status == ApplicationStatus.INTERVIEW,
            Application.interviewScheduledAt.isnot(None),
            Application.interviewScheduledAt >= datetime.now(),
            Application.interviewScheduledAt <= week_ahead,
        ),
    ), 200
