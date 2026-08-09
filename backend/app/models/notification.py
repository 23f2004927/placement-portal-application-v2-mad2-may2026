# 9 aug 26
# Christiano Fernandes
# notification.py
# in-app notification model
#
# Celery jobs write rows here instead of sending email. The UI reads them from
# a bell in the topbar, so a scheduled job produces something you can SEE.
# Email is a later delivery channel for the same rows, not a replacement.


from app.extensions import db


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    userId = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    title = db.Column(db.String(150), nullable=False)
    body = db.Column(db.Text, nullable=True)

    createdAt = db.Column(db.DateTime, server_default=db.func.now())
    readAt = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", backref="notifications")
