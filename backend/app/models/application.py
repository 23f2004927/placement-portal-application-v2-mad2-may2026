# 4 aug 26 updated
# Christiano Fernandes
# application.py
# application model


import enum

from app.extensions import db


class ApplicationStatus(enum.Enum):
    APPLIED = "applied"
    SHORTLISTED = "shortlisted"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    PLACED = "placed"


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    studentId = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    driveId = db.Column(db.Integer, db.ForeignKey("drive.id"), nullable=False)

    status = db.Column(db.Enum(ApplicationStatus), nullable=False, default=ApplicationStatus.APPLIED)

    appliedAt = db.Column(db.DateTime, server_default=db.func.now())
    statusUpdatedAt = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    interviewScheduledAt = db.Column(db.DateTime, nullable=True)
    feedback = db.Column(db.Text, nullable=True)


    joiningDate = db.Column(db.Date, nullable=True)
    finalSalary = db.Column(db.Float, nullable=True)

    student = db.relationship("Student", backref="applications")
    drive = db.relationship("Drive", backref="applications")

    __table_args__ = (
        db.UniqueConstraint("studentId", "driveId", name="uix_student_drive"),
    )
