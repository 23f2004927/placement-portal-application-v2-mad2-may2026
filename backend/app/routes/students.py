# 8 aug 26
# Christiano Fernandes
# students.py
# /api/admin/students — the candidate register
#
# Students register APPROVED, so there is nothing to review here. The only admin
# lever is the blacklist, which lives on User exactly as it does for companies.


from flask import Blueprint, jsonify, request
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models import Student
from app.policies import account_capabilities_for, can_blacklist
from app.serializers import serialize_student
from app.utils.caching import cached_payload, invalidate, scoped_key
from app.utils.decorators import role_required
from app.utils.pagination import paginate, search, sort

students_bp = Blueprint("students", __name__, url_prefix="/api")


@students_bp.route("/admin/students", methods=["GET"])
@role_required("admin")
def list_students():
    def build():
        query = Student.query.options(joinedload(Student.user))
        query = search(query, [Student.name, Student.rollNumber, Student.email, Student.phoneNumber])
        # Student.id is the tiebreaker: two students can share a name, and
        # without it those rows can swap between pages.
        query = sort(
            query,
            {
                "name": Student.name,
                "rollNumber": Student.rollNumber,
                "branch": Student.branch,
                "yearStudy": Student.yearStudy,
                "cgpa": Student.cgpa,
                "email": Student.email,
            },
            default=(Student.name, Student.id),
        )

        students, meta = paginate(query)
        return {
            "items": [serialize_student(s, "admin") for s in students],
            "capabilities": account_capabilities_for("admin", review=False),
            **meta,
        }

    return jsonify(cached_payload(scoped_key("students", per_user=False), build)), 200


@students_bp.route("/admin/students/<int:student_id>", methods=["PATCH"])
@role_required("admin")
def moderate_student(student_id):
    student = db.session.get(Student, student_id)
    if student is None:
        return jsonify(message="Student not found."), 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(message="Invalid request body."), 400

    if "blackListed" in data:
        value = data["blackListed"]
        if not isinstance(value, bool):
            return jsonify(message="blackListed must be true or false."), 400

        if not can_blacklist(student.user, "admin"):
            return jsonify(message="This account cannot be blacklisted."), 403

        student.user.blackListed = value

    db.session.commit()
    invalidate("students")

    return jsonify(serialize_student(student, "admin")), 200
