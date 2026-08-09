# 9 aug 26
# Christiano Fernandes
# notifications.py
# /api/notifications — what the Celery jobs produced, read by the topbar bell
#
# Not cached: it changes per user on every write, and it is the one screen where
# stale data would be actively misleading.


from flask import Blueprint, jsonify

from app.extensions import db
from app.models import Notification
from app.utils.decorators import role_required
from app.utils.identity import current_user_id

notifications_bp = Blueprint("notifications", __name__, url_prefix="/api")

# Any logged-in role has a bell.
ALL_ROLES = ("admin", "company", "student")


@notifications_bp.route("/notifications", methods=["GET"])
@role_required(*ALL_ROLES)
def list_notifications():
    rows = (
        Notification.query.filter_by(userId=current_user_id())
        .order_by(Notification.createdAt.desc())
        .limit(50)
        .all()
    )

    return jsonify(
        items=[
            {
                "id": n.id,
                "title": n.title,
                "body": n.body,
                "createdAt": n.createdAt.isoformat() if n.createdAt else None,
                "read": n.readAt is not None,
            }
            for n in rows
        ],
        unread=sum(1 for n in rows if n.readAt is None),
    ), 200


@notifications_bp.route("/notifications/read", methods=["POST"])
@role_required(*ALL_ROLES)
def mark_all_read():
    Notification.query.filter_by(userId=current_user_id(), readAt=None).update(
        {"readAt": db.func.now()}, synchronize_session=False
    )
    db.session.commit()
    return jsonify(message="Marked as read."), 200
