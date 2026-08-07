# 7 aug 26
# Christiano Fernandes
# profile.py
# /api/student/profile and /api/company/profile
#
# Two endpoints rather than one /api/profile branching on role, for the same
# reason registration is split: different table, different fields, different
# validation. The role is a code constant here, never read from the body.


from flask import Blueprint, jsonify, request

from app.extensions import IntegrityError, db
from app.models import Branch
from app.serializers import serialize_company, serialize_student
from app.utils.decorators import role_required
from app.utils.errors import unique_conflict
from app.utils.identity import current_company, current_student

profile_bp = Blueprint("profile", __name__, url_prefix="/api")


def _clean(data, key):
    """Trim, and treat a blank string as absent. Never applied to passwords."""
    value = data.get(key)
    return value.strip() if isinstance(value, str) else value


def _commit(serialize, row):
    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        return jsonify(
            message="Some details are already registered.",
            errors=unique_conflict(exc),
        ), 409
    return jsonify(serialize(row)), 200


@profile_bp.route("/student/profile", methods=["GET"])
@role_required("student")
def get_student_profile():
    student = current_student()
    if student is None:
        return jsonify(message="No student profile for this account."), 403
    return jsonify(serialize_student(student)), 200


@profile_bp.route("/student/profile", methods=["PATCH"])
@role_required("student")
def update_student_profile():
    student = current_student()
    if student is None:
        return jsonify(message="No student profile for this account."), 403

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(message="Invalid request body."), 400

    # rollNumber is deliberately absent: it identifies the student to the
    # institute, so it is not self-editable.
    for field in ("name", "email", "phoneNumber", "yearStudy"):
        if field in data:
            value = _clean(data, field)
            if not value:
                return jsonify(message=f"{field} cannot be blank."), 400
            setattr(student, field, value)

    if "branch" in data:
        try:
            student.branch = Branch(data["branch"])
        except ValueError:
            return jsonify(message="Unknown branch."), 400

    if "gradeYear" in data:
        raw = data["gradeYear"]
        try:
            student.gradeYear = int(raw) if raw not in (None, "") else None
        except (TypeError, ValueError):
            return jsonify(message="Invalid graduation year."), 400

    if "cgpa" in data:
        try:
            student.cgpa = float(data["cgpa"])
        except (TypeError, ValueError):
            return jsonify(message="Invalid CGPA."), 400

    if "links" in data:
        links = data["links"]
        if not isinstance(links, dict):
            return jsonify(message="Links must be an object."), 400
        student.links = {k: v.strip() for k, v in links.items() if isinstance(v, str) and v.strip()}

    if "resume" in data:
        student.resume = _clean(data, "resume") or None

    return _commit(serialize_student, student)


@profile_bp.route("/company/profile", methods=["GET"])
@role_required("company")
def get_company_profile():
    company = current_company()
    if company is None:
        return jsonify(message="No company profile for this account."), 403
    return jsonify(serialize_company(company)), 200


@profile_bp.route("/company/profile", methods=["PATCH"])
@role_required("company")
def update_company_profile():
    company = current_company()
    if company is None:
        return jsonify(message="No company profile for this account."), 403

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(message="Invalid request body."), 400

    # All NOT NULL on the model, so a blank is a 400 rather than a stored "".
    for field in ("name", "industry", "hrContactName", "hrContactEmail", "website"):
        if field in data:
            value = _clean(data, field)
            if not value:
                return jsonify(message=f"{field} cannot be blank."), 400
            setattr(company, field, value)

    if "location" in data:
        company.location = _clean(data, "location") or None

    return _commit(serialize_company, company)
