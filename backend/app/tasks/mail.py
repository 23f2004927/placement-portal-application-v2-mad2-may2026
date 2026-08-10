# 10 aug 26
# Christiano Fernandes
# mail.py
# the outbound email channel
#
# Its own task rather than a function call inside the jobs, for two reasons:
# an SMTP server being slow must not hold up a loop over sixty students, and a
# mail server being DOWN must never roll back the notification row that goes
# with it. Failure is per-message and isolated.
#
# Transport is chosen by config, not by code:
#   SMTP_HOST set    -> a real send
#   SMTP_HOST unset  -> the message is written to instance/outbox/ as .eml
#
# The outbox is not a stub. It writes the exact MIME the server would have
# sent, so the job is demonstrable on a laptop with no mail account, and
# switching to a real server is one environment variable.


import os
import smtplib
from datetime import datetime
from email.message import EmailMessage

from celery import shared_task
from flask import current_app


def outbox_dir():
    path = os.path.join(current_app.instance_path, "outbox")
    os.makedirs(path, exist_ok=True)
    return path


def _build(to, subject, html):
    message = EmailMessage()
    message["From"] = current_app.config["MAIL_FROM"]
    message["To"] = to
    message["Subject"] = subject
    # A plain-text part first, then the HTML alternative: a reader that cannot
    # render HTML still gets something, which is what multipart/alternative is for.
    message.set_content("This message is best viewed in an HTML-capable mail reader.")
    message.add_alternative(html, subtype="html")
    return message


@shared_task(name="mail.send_email")
def send_email(to, subject, html):
    """Args are plain strings — no model instances, no ids to re-fetch. That is
    what makes it safe to enqueue this before the caller's commit."""
    message = _build(to, subject, html)
    host = current_app.config.get("SMTP_HOST")

    if not host:
        safe = to.replace("@", "_at_").replace("/", "_")
        filename = f"{datetime.now():%Y%m%d-%H%M%S-%f}-{safe}.eml"
        with open(os.path.join(outbox_dir(), filename), "w", encoding="utf-8") as handle:
            handle.write(message.as_string())
        return {"to": to, "transport": "outbox", "file": filename}

    with smtplib.SMTP(host, current_app.config["SMTP_PORT"], timeout=20) as server:
        server.starttls()
        user = current_app.config.get("SMTP_USER")
        if user:
            server.login(user, current_app.config["SMTP_PASSWORD"])
        server.send_message(message)

    return {"to": to, "transport": "smtp"}
