# 10 aug 26
# Christiano Fernandes
# analytics.py
# aggregate series for the charts, plus the pre-login public dashboard
#
# Everything here is COUNTS ONLY — no names, no emails, no per-student rows.
# /api/public/stats has no @jwt_required at all, so that rule is the security
# boundary, not a convention.


from collections import Counter
from datetime import date

from flask import Blueprint, jsonify
from sqlalchemy import func

from app.extensions import cache, db
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
from app.utils.caching import cached_payload, scoped_key
from app.utils.decorators import role_required

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api")

MONTHS = 6
FUNNEL = [
    ApplicationStatus.APPLIED,
    ApplicationStatus.SHORTLISTED,
    ApplicationStatus.INTERVIEW,
    ApplicationStatus.OFFER,
    ApplicationStatus.PLACED,
]


def _recent_months(count=MONTHS):
    """['2026-03', ..., '2026-08'] ending with the current month."""
    today = date.today()
    months = []
    year, month = today.year, today.month
    for _ in range(count):
        months.append(f"{year:04d}-{month:02d}")
        month -= 1
        if month == 0:
            year, month = year - 1, 12
    return list(reversed(months))


def _monthly(column, *filters):
    """Counts grouped by YYYY-MM, zero-filled so the x-axis has no gaps.

    Zero-filling matters: without it a quiet month is missing rather than zero,
    and a line chart would join across the gap and imply activity that never
    happened.
    """
    rows = (
        db.session.query(func.strftime("%Y-%m", column), func.count(Application.id))
        .filter(*filters)
        .group_by(func.strftime("%Y-%m", column))
        .all()
    )
    found = dict(rows)
    return [found.get(m, 0) for m in _recent_months()]


def _funnel(*filters):
    counts = dict(
        db.session.query(Application.status, func.count(Application.id))
        .filter(*filters)
        .group_by(Application.status)
        .all()
    )
    return [
        {"stage": status.value, "count": counts.get(status, 0)} for status in FUNNEL
    ]


def _offer_outcomes(*filters):
    """What happened to offers once they were made.

    Only answerable since DECLINED existed: before that a student turning an
    offer down was indistinguishable from the company rejecting them.
    """
    counts = dict(
        db.session.query(Application.status, func.count(Application.id))
        .filter(*filters)
        .group_by(Application.status)
        .all()
    )
    return [
        {"outcome": "accepted", "count": counts.get(ApplicationStatus.PLACED, 0)},
        {"outcome": "declined", "count": counts.get(ApplicationStatus.DECLINED, 0)},
        {"outcome": "awaiting", "count": counts.get(ApplicationStatus.OFFER, 0)},
    ]


def _placements_by_branch(limit=8):
    """18 branches will not fit on an axis, so the tail folds into 'other'
    rather than being generated a colour it cannot be told apart by."""
    rows = (
        db.session.query(Student.branch, func.count(Application.id))
        .join(Application, Application.studentId == Student.id)
        .filter(Application.status == ApplicationStatus.PLACED)
        .group_by(Student.branch)
        .all()
    )
    tallied = sorted(
        ((b.value.replace("_", " "), n) for b, n in rows if b), key=lambda r: -r[1]
    )
    head, tail = tallied[:limit], tallied[limit:]
    if tail:
        head.append(("other", sum(n for _, n in tail)))
    return [{"branch": b, "count": n} for b, n in head]


def _top_skills(limit=8, *filters):
    """skillsRequired is a JSON array, so SQLite cannot group it. The list is
    small enough to tally in Python; revisit if drives ever reach thousands."""
    tally = Counter()
    for (skills,) in db.session.query(Drive.skillsRequired).filter(*filters).all():
        for skill in skills or []:
            cleaned = str(skill).strip().lower()
            if cleaned:
                tally[cleaned] += 1
    return [{"skill": s, "count": n} for s, n in tally.most_common(limit)]


@analytics_bp.route("/admin/analytics", methods=["GET"])
@role_required("admin")
def admin_analytics():
    """Cached for 5 minutes — unlike /api/admin/stats, which stays live.

    Nobody needs second-accurate aggregates, and no invalidation is wired on
    purpose: the TTL is the whole policy. Trends move slowly; queues do not,
    which is why the two live in different endpoints.
    """

    def build():
        return {
            "months": _recent_months(),
            "applications": _monthly(Application.appliedAt),
            # NOTE: approximate. statusUpdatedAt holds only the LAST change, so
            # editing a placed row later moves it into the wrong month. Exact
            # history needs an event log.
            "placements": _monthly(
                Application.statusUpdatedAt,
                Application.status == ApplicationStatus.PLACED,
            ),
            "funnel": _funnel(),
            "topSkills": _top_skills(),
            "offerOutcomes": _offer_outcomes(),
            "placementsByBranch": _placements_by_branch(),
        }

    # per_user=False: every admin sees the same portal-wide figures.
    return jsonify(cached_payload(scoped_key("adminAnalytics", per_user=False), build, ttl=300)), 200


@analytics_bp.route("/company/analytics", methods=["GET"])
@role_required("company")
def company_analytics():
    from app.utils.identity import current_company

    company = current_company()
    if company is None:
        return jsonify(message="No company profile for this account."), 403

    # An application reaches a company only through its drives, so every filter
    # here joins rather than touching Application directly.
    mine = Application.driveId.in_(
        db.session.query(Drive.id).filter(Drive.companyId == company.id)
    )

    def build():
        return {
            "months": _recent_months(),
            "applications": _monthly(Application.appliedAt, mine),
            "placements": _monthly(
                Application.statusUpdatedAt, mine, Application.status == ApplicationStatus.PLACED
            ),
            "funnel": _funnel(mine),
            "topSkills": _top_skills(8, Drive.companyId == company.id),
            "offerOutcomes": _offer_outcomes(mine),
        }

    # per_user=True here: these figures are scoped to the caller's own company.
    return jsonify(cached_payload(scoped_key("companyAnalytics"), build, ttl=300)), 200


@analytics_bp.route("/public/stats", methods=["GET"])
def public_stats():
    """No authentication — deliberately. Cached for 5 minutes because it is the
    only endpoint an anonymous visitor can hit, so it is the only one where
    traffic is unbounded."""
    payload = cache.get("public:stats")
    if payload is None:
        payload = {
            "students": db.session.query(func.count(Student.id)).scalar() or 0,
            "companies": db.session.query(func.count(Company.id))
            .join(User, Company.userId == User.id)
            .filter(User.accountStatus == AccountStatus.APPROVED)
            .scalar()
            or 0,
            "openDrives": db.session.query(func.count(Drive.id))
            .filter(Drive.status == DriveStatus.APPROVED)
            .scalar()
            or 0,
            "placed": db.session.query(func.count(Application.id))
            .filter(Application.status == ApplicationStatus.PLACED)
            .scalar()
            or 0,
            "months": _recent_months(),
            "placements": _monthly(
                Application.statusUpdatedAt,
                Application.status == ApplicationStatus.PLACED,
            ),
        }
        cache.set("public:stats", payload, timeout=300)

    return jsonify(payload), 200
