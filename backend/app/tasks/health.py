# 8 aug 26
# Christiano Fernandes
# health.py
# one trivial task, used to prove the wiring before any real job is written


from celery import shared_task

from app.extensions import db
from app.models import User


@shared_task(name="health.ping")
def ping():
    """Returns a row count, so a success proves both halves: the broker reached
    the worker, and the worker had an app context to query in."""
    return {"ok": True, "users": db.session.query(User).count()}

@shared_task(name="health.boom")
def boom():
    return 1 / 0
