# 4 aug 26 updated
# Christiano Fernandes
# drive.py
# drive model


import enum

from app.extensions import db
from app.models.student import Branch


class JobType(enum.Enum):
    FULL_TIME = "full_time"
    INTERNSHIP = "internship"
    PPO = "ppo"


class DriveStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    CLOSED = "closed"


class Drive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    companyId = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)

    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)


    branch = db.Column(db.Enum(Branch), nullable=True)
    minCgpa = db.Column(db.Float, nullable=True)
    eligibleYear = db.Column(db.Integer, nullable=True)
    skillsRequired = db.Column(db.JSON, nullable=True)

    # Stated as text ("0-1 years", "Fresher") rather than a number: postings
    # phrase it as a range, and nothing here filters on it.
    experienceRequired = db.Column(db.String(100), nullable=True)

    salary = db.Column(db.Float, nullable=True)
    benefits = db.Column(db.Text, nullable=True)
    numOpenings = db.Column(db.Integer, nullable=True)
    jobType = db.Column(db.Enum(JobType), nullable=True)

    applicationDeadline = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Enum(DriveStatus), nullable=False, default=DriveStatus.PENDING)

    createdAt = db.Column(db.DateTime, server_default=db.func.now())
    updatedAt = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    company = db.relationship("Company", backref="drives")
