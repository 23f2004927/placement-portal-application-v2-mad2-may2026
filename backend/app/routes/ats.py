# 10 aug 26
# Christiano Fernandes
# ats.py
# /api/ats/screen — keyword match between a resume and a drive's skill list
#
# Deliberately simple, and honest about it: this is exact keyword matching, not
# semantic matching. "React" matches "react"; it does not match "front-end".
# The score is a hint for a human, never a decision — nothing in the portal
# reads it, and no application status depends on it.
#
# Plain text only. Parsing PDFs would need a library outside the permitted
# stack, so the caller pastes the text.


import re

from flask import Blueprint, jsonify, request

from app.extensions import db
from app.models import Drive, DriveStatus
from app.utils.decorators import role_required
from app.utils.identity import current_company, current_role

ats_bp = Blueprint("ats", __name__, url_prefix="/api")

MAX_RESUME_CHARS = 20000


def _tokens(text):
    """Lowercased word set. Splitting on non-word characters means 'node.js'
    contributes 'node' and 'js', which is what makes multi-word skills work."""
    return set(re.split(r"[^a-z0-9+#]+", text.lower())) - {""}


def _matches(skill, resume_tokens, resume_text):
    """A multi-word skill ('machine learning') is matched as a phrase; a single
    word is matched against the token set so 'java' never matches 'javascript'."""
    skill = skill.strip().lower()
    if not skill:
        return False
    if " " in skill:
        return skill in resume_text
    return skill in resume_tokens


@ats_bp.route("/ats/screen", methods=["POST"])
@role_required("student", "company")
def screen():
    data = request.get_json(silent=True) or {}
    resume_text = (data.get("resumeText") or "").strip()
    drive_id = data.get("driveId")

    if not resume_text:
        return jsonify(message="Paste the resume text to screen."), 400
    if len(resume_text) > MAX_RESUME_CHARS:
        return jsonify(message="That resume is too long to screen."), 400
    if not drive_id:
        return jsonify(message="Choose a drive to screen against."), 400

    drive = db.session.get(Drive, drive_id)
    if drive is None:
        return jsonify(message="Drive not found."), 404

    # Same visibility rules as everywhere else: a company screens only against
    # its own drives, a student only against drives it could actually apply to.
    role = current_role()
    if role == "company":
        company = current_company()
        if company is None or drive.companyId != company.id:
            return jsonify(message="Drive not found."), 404
    elif drive.status != DriveStatus.APPROVED:
        return jsonify(message="Drive not found."), 404

    skills = [str(s).strip() for s in (drive.skillsRequired or []) if str(s).strip()]
    if not skills:
        return jsonify(
            driveTitle=drive.title,
            score=None,
            matched=[],
            missing=[],
            message="This drive lists no required skills, so there is nothing to match.",
        ), 200

    tokens = _tokens(resume_text)
    lowered = resume_text.lower()

    matched = [s for s in skills if _matches(s, tokens, lowered)]
    missing = [s for s in skills if s not in matched]

    return jsonify(
        driveTitle=drive.title,
        score=round(len(matched) / len(skills) * 100),
        matched=matched,
        missing=missing,
    ), 200
