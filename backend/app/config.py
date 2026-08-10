# 4 aug 26 updated
# Christiano Fernandes
# config.py
# app configuration (db path, secrets)


import os

from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
os.makedirs(INSTANCE_DIR, exist_ok=True)


REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = os.environ.get("REDIS_PORT", "6379")
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"


class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(INSTANCE_DIR, "ppa.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-secret-change-me")

    # Caps the request BODY, so an oversized upload is refused before Flask
    # buffers it. Global — it applies to JSON posts too, which is harmless.
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024

    # Separate Redis databases on purpose: flushing the cache must never be able
    # to drop queued jobs or their results.
    #   /0 broker · /1 results · /2 cache
    CELERY = dict(
        broker_url=f"{REDIS_URL}/0",
        result_backend=f"{REDIS_URL}/1",
        timezone="Asia/Kolkata",
        task_ignore_result=False,
        broker_connection_retry_on_startup=True,
        # "task" must match @shared_task(name=...) exactly — beat sends a name
        # string, it never imports the function.
        beat_schedule={
            "daily-student-reminders": {
                "task": "reminders.daily_student_reminders",
                "schedule": crontab(hour=9, minute=0),
            },
            "monthly-placement-report": {
                "task": "reports.monthly_placement_report",
                "schedule": crontab(day_of_month=1, hour=7, minute=0),
            },
        },
    )

    # Mail. With SMTP_HOST unset the send_email task writes the message to
    # instance/outbox/ instead, so the scheduled jobs are demonstrable without
    # a mail account. Setting the host is the only change needed to go live.
    SMTP_HOST = os.environ.get("SMTP_HOST")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
    SMTP_USER = os.environ.get("SMTP_USER")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
    MAIL_FROM = os.environ.get("MAIL_FROM", "placement-cell@institute.edu")

    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = f"{REDIS_URL}/2"
    CACHE_DEFAULT_TIMEOUT = 300
