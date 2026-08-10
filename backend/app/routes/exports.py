# 9 aug 26
# Christiano Fernandes
# exports.py
# /api/exports — the user-triggered asynchronous job
#
# Three steps, because the work does not finish inside the request:
#   POST /api/exports/applications   -> 202 { taskId }   the job is queued
#   GET  /api/exports/<taskId>       -> 200 { state }    the browser polls
#   GET  /api/exports/<taskId>/file  -> the CSV          once state is SUCCESS
#
# 202 Accepted, not 200 OK: the request was valid and accepted, but there is
# nothing to return yet.


import os

from flask import Blueprint, current_app, jsonify, send_from_directory

from app.tasks.exports import company_applications_csv, export_dir, student_applications_csv
from app.utils.decorators import role_required
from app.utils.identity import current_role, current_user_id

exports_bp = Blueprint("exports", __name__, url_prefix="/api")

# Which task each role's export runs. The role comes from the signed claim, so
# a company cannot ask for the student export or the reverse.
TASK_FOR_ROLE = {
    "student": student_applications_csv,
    "company": company_applications_csv,
}


def _owned_result(task_id):
    """The task's own return value carries the userId that asked for it, so
    ownership is checked without a second table. Without this any logged-in
    user could read another's export by guessing a task id."""
    result = current_app.extensions["celery"].AsyncResult(task_id)
    if not result.successful():
        return result, None

    payload = result.result or {}
    if payload.get("userId") != current_user_id():
        return result, None
    return result, payload


@exports_bp.route("/exports/applications", methods=["POST"])
@role_required("student", "company")
def start_export():
    task = TASK_FOR_ROLE[current_role()].delay(current_user_id())
    return jsonify(taskId=task.id), 202


@exports_bp.route("/exports/<task_id>", methods=["GET"])
@role_required("student", "company")
def export_state(task_id):
    result, payload = _owned_result(task_id)

    if result.failed():
        return jsonify(state="FAILURE"), 200
    if result.successful():
        if payload is None:
            return jsonify(message="Export not found."), 404
        return jsonify(state="SUCCESS", rows=payload.get("rows", 0)), 200

    # PENDING here means "no record of this id" — Celery writes nothing until a
    # task starts, so an unknown id looks exactly like a queued one.
    return jsonify(state=result.state), 200


@exports_bp.route("/exports/<task_id>/file", methods=["GET"])
@role_required("student", "company")
def export_file(task_id):
    result, payload = _owned_result(task_id)
    if not result.successful() or payload is None:
        return jsonify(message="Export not found."), 404

    directory = export_dir()
    if not os.path.exists(os.path.join(directory, payload["filename"])):
        return jsonify(message="Export file has been cleaned up."), 404

    return send_from_directory(
        directory,
        payload["filename"],
        as_attachment=True,
        download_name="applications.csv",
    )
