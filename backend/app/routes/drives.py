# 7 aug 26
# Christiano Fernandes
# drives.py
# /api/drives — same shared-endpoint pattern as applications


from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy.orm import joinedload, selectinload

from app.extensions import db
from app.models import (
    Application,
    ApplicationStatus,
    Branch,
    Company,
    Drive,
    DriveStatus,
    JobType,
)
from app.policies import (
    STUDENT_VISIBLE_DRIVES,
    can_close_drive,
    can_edit_drive,
    can_moderate_drive,
    drive_capabilities_for,
)
from app.serializers import serialize_drive
from app.utils.caching import cached_payload, invalidate, scoped_key
from app.utils.decorators import role_required
from app.utils.pagination import enum_filter, paginate, search, sort
from app.utils.identity import current_company, current_role, current_student

drives_bp = Blueprint("drives", __name__, url_prefix="/api")


def _parse_deadline(raw):
    """Returns (value, error). datetime-local sends 'YYYY-MM-DDTHH:mm'."""
    if not raw:
        return None, None
    try:
        return datetime.fromisoformat(raw), None
    except (TypeError, ValueError):
        return None, "Invalid application deadline."


def _coerce_number(raw, cast):
    if raw in (None, ""):
        return None, None
    try:
        return cast(raw), None
    except (TypeError, ValueError):
        return None, "Expected a number."


def _apply_payload(drive, data):
    """Writes the editable columns. Returns an error message or None."""
    if "title" in data:
        title = (data["title"] or "").strip()
        if not title:
            return "Title is required."
        drive.title = title

    for field in ("description", "experienceRequired", "benefits"):
        if field in data:
            setattr(drive, field, (data[field] or "").strip() or None)

    if "jobType" in data:
        try:
            drive.jobType = JobType(data["jobType"]) if data["jobType"] else None
        except ValueError:
            return "Unknown job type."

    if "branch" in data:
        try:
            drive.branch = Branch(data["branch"]) if data["branch"] else None
        except ValueError:
            return "Unknown branch."

    for field, cast in (
        ("minCgpa", float),
        ("salary", float),
        ("eligibleYear", int),
        ("numOpenings", int),
    ):
        if field in data:
            value, error = _coerce_number(data[field], cast)
            if error:
                return f"{field}: {error}"
            setattr(drive, field, value)

    if "skillsRequired" in data:
        skills = data["skillsRequired"] or []
        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(",")]
        drive.skillsRequired = [s for s in skills if s]

    if "applicationDeadline" in data:
        value, error = _parse_deadline(data["applicationDeadline"])
        if error:
            return error
        drive.applicationDeadline = value

    return None


@drives_bp.route("/drives", methods=["GET"])
@jwt_required()
def list_drives():
    """Three scopes, same resource. The student branch is the interesting one:
    it also applies the drive's own eligibility rules, so the list matches what
    the student can actually act on."""
    role = current_role()

    # Identity is resolved BEFORE the cache is consulted, so a caller with no
    # profile row still gets a 403 rather than a cached body.
    company = student = None
    if role == "company":
        company = current_company()
        if company is None:
            return jsonify(message="No company profile for this account."), 403
    elif role == "student":
        student = current_student()
        if student is None:
            return jsonify(message="No student profile for this account."), 403
    elif role != "admin":
        return jsonify(message="Forbidden"), 403

    # Keyed per role AND per user: the student branch filters by that student's
    # own eligibility, so a shared key would serve one student another's list.
    # 60s TTL, plus an explicit version bump on every drive write.
    payload = cached_payload(
        scoped_key("drives"),
        lambda: _build_drives_payload(role, company, student),
    )
    return jsonify(payload), 200


def _build_drives_payload(role, company, student):
    query = Drive.query.options(joinedload(Drive.company)).join(Drive.company)
    applied_ids = None

    if role == "company":
        query = query.options(selectinload(Drive.applications)).filter(
            Drive.companyId == company.id
        )

    elif role == "student":
        query = query.filter(Drive.status.in_(STUDENT_VISIBLE_DRIVES))

        # Closed postings are not opportunities.
        query = query.filter(
            (Drive.applicationDeadline.is_(None)) | (Drive.applicationDeadline >= datetime.now())
        )

        # Branch / CGPA / year are NOT filtered here. They are the company's
        # stated preference, not a rule the portal enforces — and the apply
        # endpoint never checked them, so filtering the list only hid
        # information without preventing anything. The serializer annotates
        # each row with `eligible` and `ineligibleReasons` instead.

        # One query for the whole page rather than one per row.
        applied_ids = {
            row[0]
            for row in db.session.query(Application.driveId)
            .filter(Application.studentId == student.id)
            .all()
        }

        # ?applied=yes|no — "have I already put my name down for this?"
        applied = (request.args.get("applied") or "").strip()
        if applied == "yes":
            query = query.filter(Drive.id.in_(applied_ids or [-1]))
        elif applied == "no":
            query = query.filter(Drive.id.notin_(applied_ids or [-1]))

        # ?maxCgpa= — drives asking for at most this. A drive with no minimum
        # always qualifies, which is why NULL is kept rather than compared.
        raw_cgpa = (request.args.get("maxCgpa") or "").strip()
        if raw_cgpa:
            try:
                query = query.filter(
                    (Drive.minCgpa.is_(None)) | (Drive.minCgpa <= float(raw_cgpa))
                )
            except ValueError:
                pass

    elif role == "admin":
        query = query.options(selectinload(Drive.applications))

    # skillsRequired is JSON, which SQLite stores as text — so ilike matches
    # inside the array without a JSON function or an extra table. Crude, and
    # it means "java" also matches "javascript"; acceptable for a search box,
    # which is a way to narrow a list rather than an exact filter.
    query = search(query, [Drive.title, Company.name, Drive.skillsRequired])
    query = enum_filter(query, Drive.status, DriveStatus)
    query = sort(
        query,
        {
            "title": Drive.title,
            "companyName": Company.name,
            "jobType": Drive.jobType,
            "minCgpa": Drive.minCgpa,
            "salary": Drive.salary,
            "numOpenings": Drive.numOpenings,
            "applicationDeadline": Drive.applicationDeadline,
            "status": Drive.status,
        },
        default=(Drive.createdAt.desc(), Drive.id.desc()),
    )

    drives, meta = paginate(query)

    return {
        "items": [serialize_drive(d, role, applied_ids, student) for d in drives],
        "capabilities": drive_capabilities_for(role),
        **meta,
    }


@drives_bp.route("/drives/<int:drive_id>", methods=["GET"])
@jwt_required()
def get_drive(drive_id):
    role = current_role()
    drive = db.session.get(Drive, drive_id)

    if drive is None:
        return jsonify(message="Drive not found."), 404

    if role == "company":
        company = current_company()
        if company is None or drive.companyId != company.id:
            return jsonify(message="Drive not found."), 404
    elif role == "student" and drive.status not in STUDENT_VISIBLE_DRIVES:
        return jsonify(message="Drive not found."), 404
    elif role not in ("company", "student", "admin"):
        return jsonify(message="Forbidden"), 403

    return jsonify(
        serialize_drive(drive, role, set(), current_student() if role == "student" else None)
    ), 200


# approved=True is the real gate on a pending company, and this is the only
# place one can be applied: every other company write requires owning a drive,
# which a company that has never been approved cannot have.
@drives_bp.route("/drives", methods=["POST"])
@role_required("company", approved=True)
def create_drive():
    company = current_company()
    if company is None:
        return jsonify(message="No company profile for this account."), 403

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(message="Invalid request body."), 400

    # Status is not client-settable: every posting starts awaiting review.
    drive = Drive(companyId=company.id, title="", status=DriveStatus.PENDING)

    error = _apply_payload(drive, data)
    if error:
        return jsonify(message=error), 400

    db.session.add(drive)
    db.session.commit()
    invalidate("drives")

    return jsonify(serialize_drive(drive, "company", set())), 201


@drives_bp.route("/drives/<int:drive_id>", methods=["PATCH"])
@jwt_required()
def update_drive(drive_id):
    """Company edits content; admin moderates status. Both land here because
    they are the same resource — the role decides which half is writable."""
    role = current_role()
    drive = db.session.get(Drive, drive_id)

    if drive is None:
        return jsonify(message="Drive not found."), 404

    if role == "company":
        company = current_company()
        if company is None or drive.companyId != company.id:
            return jsonify(message="Drive not found."), 404
    elif role != "admin":
        return jsonify(message="Forbidden"), 403

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(message="Invalid request body."), 400

    if "status" in data:
        try:
            new_status = DriveStatus(data["status"])
        except ValueError:
            return jsonify(message="Unknown status."), 400

        if new_status == DriveStatus.CLOSED:
            if not can_close_drive(drive, role):
                return jsonify(message="This drive cannot be closed."), 409
        elif not can_moderate_drive(drive, role):
            return jsonify(message="That status change is not allowed."), 409

        drive.status = new_status

    content_fields = set(data) - {"status"}
    if content_fields:
        if not can_edit_drive(drive, role):
            return jsonify(message="This drive can no longer be edited."), 409
        error = _apply_payload(drive, data)
        if error:
            return jsonify(message=error), 400

    db.session.commit()
    invalidate("drives")

    return jsonify(serialize_drive(drive, role, set())), 200
