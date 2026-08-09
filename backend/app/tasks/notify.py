# 9 aug 26
# Christiano Fernandes
# notify.py
# the one place a notification is created
#
# Every job funnels through notify() rather than writing Notification rows
# itself. That keeps the delivery channel in ONE function: adding email later
# means editing the marked block below and nothing else.


from app.extensions import db
from app.models import Notification


def notify(user_id, title, body=None):
    """Create an in-app notification. Caller commits."""
    db.session.add(Notification(userId=user_id, title=title, body=body))

    # --- PROVISION: email delivery -------------------------------------
    # When Flask-Mail is added, the line below is the whole integration:
    #
    #     from app.tasks.mail import send_email
    #     send_email.delay(user_email, title, body)
    #
    # It is a separate task on purpose — a mail server being down must never
    # roll back the notification row, and the caller must not wait for SMTP.
    # -------------------------------------------------------------------
