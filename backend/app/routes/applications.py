# 7 aug 26
# Christiano Fernandes
# applications.py
# /api/applications — one resource, scoped three ways by JWT claim


from datetime import date, datetime

from flask import Blueprint, Response, jsonify, render_template, request
from flask_jwt_extended import jwt_required
from sqlalchemy.orm import joinedload

from app.extensions import IntegrityError, db
from app.models import (
    Application,
    ApplicationStatus,
    Company,
    Drive,
    DriveStatus,
    OfferLetter,
    Placement,
    Student,
)
from app.policies import (
    HIDDEN_FROM_COMPANY,
    can_issue_offer_letter,
    can_respond_to_offer,
    can_revoke,
    can_set_status,
    capabilities_for,
    drive_ineligibility,
)
from app.serializers import serialize_application
from app.utils.caching import invalidate
from app.utils.decorators import role_required
from app.utils.pagination import enum_filter, paginate, search, sort
from app.utils.identity import current_company, current_role, current_student

# url_prefix stops at /api so every rule can carry a leading slash. A blueprint
# prefix of /api/applications plus a route of "/" would produce a trailing-slash
# URL and a 308 redirect on every call, which breaks the CORS preflight.
applications_bp = Blueprint("applications", __name__, url_prefix="/api")


def _load_owned(application_id, role):
    """Fetch an application the caller is allowed to touch, else None.

    Returns None rather than raising so callers answer 404 — a 403 would confirm
    that the id exists.
    """
    application = db.session.get(Application, application_id)
    if application is None:
        return None

    if role == "admin":
        return application

    if role == "student":
        student = current_student()
        if student is None or application.studentId != student.id:
            return None
        return application

    if role == "company":
        company = current_company()
        if company is None or application.drive.companyId != company.id:
            return None
        if application.status in HIDDEN_FROM_COMPANY:
            return None
        return application

    return None


@applications_bp.route("/applications", methods=["GET"])
@jwt_required()
def list_applications():
    """No role_required — all three roles may call this. The scoping IS the
    authorization, which is why the else-branch below is explicit: an unknown
    role must not fall through to an unfiltered query."""
    role = current_role()

    # Joined once, up front: the company branch needs Drive for ownership and
    # the search needs all three. joinedload uses its own anonymous aliases, so
    # these joins never collide with the eager loading.
    query = (
        Application.query.options(
            joinedload(Application.drive).joinedload(Drive.company),
            joinedload(Application.student),
            joinedload(Application.offerLetter),
        )
        .join(Application.drive)
        .join(Drive.company)
        .join(Application.student)
    )

    if role == "student":
        student = current_student()
        if student is None:
            return jsonify(message="No student profile for this account."), 403
        query = query.filter(Application.studentId == student.id)

    elif role == "company":
        company = current_company()
        if company is None:
            return jsonify(message="No company profile for this account."), 403
        # An Application has no companyId — ownership runs through Drive.
        query = query.filter(
            Drive.companyId == company.id,
            Application.status.notin_(HIDDEN_FROM_COMPANY),
        )

    elif role != "admin":
        return jsonify(message="Forbidden"), 403

    query = search(query, [Drive.title, Company.name, Student.name, Student.rollNumber])
    query = enum_filter(query, Application.status, ApplicationStatus)
    query = sort(
        query,
        {
            "studentName": Student.name,
            "rollNumber": Student.rollNumber,
            "cgpa": Student.cgpa,
            "driveTitle": Drive.title,
            "companyName": Company.name,
            "appliedAt": Application.appliedAt,
            "interviewScheduledAt": Application.interviewScheduledAt,
            "status": Application.status,
        },
        default=(Application.appliedAt.desc(), Application.id.desc()),
    )

    applications, meta = paginate(query)

    return jsonify(
        items=[serialize_application(a, role) for a in applications],
        capabilities=capabilities_for(role),
        **meta,
    ), 200


@applications_bp.route("/applications", methods=["POST"])
@role_required("student")
def create_application():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not data.get("driveId"):
        return jsonify(message="driveId is required."), 400

    student = current_student()
    if student is None:
        return jsonify(message="No student profile for this account."), 403

    drive = db.session.get(Drive, data["driveId"])
    # Unapproved drives are invisible to students, so "not approved" is a 404.
    if drive is None or drive.status != DriveStatus.APPROVED:
        return jsonify(message="That drive is not open for applications."), 404

    # The list already hides expired drives, but a tab left open overnight still
    # holds a live id. The list is a view; this is the guarantee.
    if drive.applicationDeadline is not None and drive.applicationDeadline < datetime.now():
        return jsonify(message="Applications for this drive have closed."), 409

    # Eligibility is enforced here, not merely annotated. The serializer runs the
    # same function so the student is told why before they click, and the two
    # answers cannot disagree — it is one function with two callers.
    reasons = drive_ineligibility(drive, student)
    if reasons:
        return jsonify(
            message="You do not meet the eligibility criteria for this drive.",
            reasons=reasons,
        ), 403

    application = Application(
        studentId=student.id,
        driveId=drive.id,
        status=ApplicationStatus.APPLIED,
    )

    try:
        db.session.add(application)
        db.session.commit()
    except IntegrityError:
        # The UniqueConstraint on (studentId, driveId) is the real guard against
        # double-applying — and against re-applying after a revoke, since the
        # revoked row is kept rather than deleted.
        db.session.rollback()
        return jsonify(message="You have already applied to this drive."), 409

    # The drive payload carries applicationCount and alreadyApplied, so applying
    # changes what /api/drives should return.
    invalidate("drives")

    return jsonify(serialize_application(application, "student")), 201


@applications_bp.route("/applications/<int:application_id>/revoke", methods=["POST"])
@jwt_required()
def revoke_application(application_id):
    role = current_role()
    application = _load_owned(application_id, role)
    if application is None:
        return jsonify(message="Application not found."), 404

    if not can_revoke(application, role):
        return jsonify(message="This application can no longer be withdrawn."), 409

    application.status = ApplicationStatus.REVOKED
    db.session.commit()
    invalidate("drives")

    return jsonify(serialize_application(application, role)), 200


@applications_bp.route("/applications/<int:application_id>/respond", methods=["POST"])
@jwt_required()
def respond_to_offer(application_id):
    """The student's answer to an offer.

    A separate verb rather than the generic PATCH, mirroring /revoke: the payload
    is one constrained choice, and it keeps PATCH company/admin-only.
    """
    role = current_role()
    application = _load_owned(application_id, role)
    if application is None:
        return jsonify(message="Application not found."), 404

    decision = (request.get_json(silent=True) or {}).get("decision")
    if decision not in ("accept", "decline"):
        return jsonify(message="Decision must be accept or decline."), 400

    new_status = (
        ApplicationStatus.PLACED if decision == "accept" else ApplicationStatus.DECLINED
    )

    if not can_respond_to_offer(application, role, new_status):
        return jsonify(message="There is no open offer to respond to."), 409

    application.status = new_status

    # Accepting is what creates the placement record. It reads from the offer
    # letter when one exists, because those are the terms the student agreed
    # to; otherwise it falls back to what the drive currently advertises.
    if new_status is ApplicationStatus.PLACED and application.placement is None:
        letter = application.offerLetter
        db.session.add(
            Placement(
                studentId=application.studentId,
                companyId=application.drive.companyId,
                applicationId=application.id,
                position=letter.roleTitle if letter else application.drive.title,
                salary=(letter.salary if letter else None) or application.drive.salary,
                joiningDate=(letter.joiningDate if letter else None) or application.joiningDate,
            )
        )

    db.session.commit()

    # Placement changes the counts the drive payload carries.
    invalidate("drives")

    return jsonify(serialize_application(application, role)), 200


@applications_bp.route("/applications/<int:application_id>/offer-letter", methods=["POST"])
@jwt_required()
def issue_offer_letter(application_id):
    role = current_role()
    application = _load_owned(application_id, role)
    if application is None:
        return jsonify(message="Application not found."), 404

    if not can_issue_offer_letter(application, role):
        return jsonify(message="An offer letter can only be issued on an offer."), 409

    if application.offerLetter is not None:
        return jsonify(message="An offer letter has already been issued."), 409

    data = request.get_json(silent=True) or {}
    joining_date = None
    if data.get("joiningDate"):
        try:
            joining_date = date.fromisoformat(data["joiningDate"])
        except (TypeError, ValueError):
            return jsonify(message="Invalid joining date."), 400

    drive = application.drive
    letter = OfferLetter(
        applicationId=application.id,
        roleTitle=drive.title,
        companyName=drive.company.name,
        jobType=drive.jobType.value if drive.jobType else None,
        location=drive.company.location,
        salary=drive.salary,
        joiningDate=joining_date,
    )

    # Mirror onto the application so the placement record matches the letter.
    application.finalSalary = drive.salary
    application.joiningDate = joining_date

    db.session.add(letter)
    db.session.commit()

    return jsonify(serialize_application(application, role)), 201


@applications_bp.route("/applications/<int:application_id>/offer-letter", methods=["GET"])
@jwt_required()
def download_offer_letter(application_id):
    """Served as an HTML attachment rather than a PDF: a PDF library is outside
    the permitted stack, and the browser can print this to PDF."""
    role = current_role()
    application = _load_owned(application_id, role)
    if application is None:
        return jsonify(message="Application not found."), 404

    letter = application.offerLetter
    if letter is None:
        return jsonify(message="No offer letter has been issued yet."), 404

    html = render_template("offer_letter.html", letter=letter, student=application.student)
    filename = f"offer-letter-{letter.applicationId}.html"

    return Response(
        html,
        mimetype="text/html",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@applications_bp.route("/applications/<int:application_id>", methods=["PATCH"])
@jwt_required()
def update_application(application_id):
    role = current_role()
    if role not in ("company", "admin"):
        return jsonify(message="Forbidden"), 403

    application = _load_owned(application_id, role)
    if application is None:
        return jsonify(message="Application not found."), 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(message="Invalid request body."), 400

    if "status" in data:
        try:
            new_status = ApplicationStatus(data["status"])
        except ValueError:
            return jsonify(message="Unknown status."), 400

        if not can_set_status(application, role, new_status):
            return jsonify(message="That status change is not allowed."), 409

        application.status = new_status

    if "feedback" in data:
        application.feedback = (data["feedback"] or "").strip() or None

    if "interviewScheduledAt" in data:
        raw = data["interviewScheduledAt"]
        if not raw:
            application.interviewScheduledAt = None
        else:
            try:
                application.interviewScheduledAt = datetime.fromisoformat(raw)
            except (TypeError, ValueError):
                return jsonify(message="Invalid interview date."), 400

    db.session.commit()

    return jsonify(serialize_application(application, role)), 200
