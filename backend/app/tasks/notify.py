# 9 aug 26
# Christiano Fernandes
# notify.py
# the one place a notification is created
#
# Every job funnels through notify() rather than writing Notification rows
# itself, so the delivery channels live in ONE function. A message goes to two
# places: the bell in the app, and — when an address is given — email.


from markupsafe import escape

from app.extensions import db
from app.models import Notification
from app.tasks.mail import send_email


def notify(user_id, title, body=None, email=None, html=None):
    """Create an in-app notification, and email it if an address is given.

    Caller commits. `html` overrides the default one-paragraph body, which is
    how the monthly report sends a full rendered document through the same door.
    """
    db.session.add(Notification(userId=user_id, title=title, body=body))

    if not email:
        return

    # Enqueued BEFORE the caller's commit, which is normally the mistake — a
    # worker can start before the row exists. It is safe here because
    # send_email takes the finished message as strings and never reads the
    # database, so there is nothing for it to race against.
    send_email.delay(email, title, html or f"<p>{escape(body or title)}</p>")
