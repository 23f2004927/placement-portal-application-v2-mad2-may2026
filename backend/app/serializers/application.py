# 7 aug 26
# Christiano Fernandes
# application.py
# Application -> JSON, shaped per viewer
#
# A function rather than Application.to_dict() because the same row is three
# different payloads: a model method has no notion of who is asking, and giving
# it one would put role logic on the model.
#
# NOTE: this reads relationships (application.drive, application.student) but
# never queries. Preventing the N+1 is the caller's job, via joinedload.


def _iso(value):
    return value.isoformat() if value else None


def serialize_application(application, viewer_role):
    drive = application.drive
    student = application.student

    data = {
        "id": application.id,
        "status": application.status.value,
        "appliedAt": _iso(application.appliedAt),
        "statusUpdatedAt": _iso(application.statusUpdatedAt),
        "interviewScheduledAt": _iso(application.interviewScheduledAt),
        "feedback": application.feedback,
        "driveId": drive.id,
        "driveTitle": drive.title,
        "companyName": drive.company.name,
    }

    # Candidate details are for the people making decisions about them.
    if viewer_role in ("company", "admin"):
        data.update(
            studentId=student.id,
            studentName=student.name,
            rollNumber=student.rollNumber,
            branch=student.branch.value if student.branch else None,
            cgpa=student.cgpa,
            email=student.email,
        )

    if viewer_role == "admin":
        data.update(joiningDate=_iso(application.joiningDate), finalSalary=application.finalSalary)

    return data
