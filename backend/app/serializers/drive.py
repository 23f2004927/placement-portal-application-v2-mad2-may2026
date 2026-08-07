# 7 aug 26
# Christiano Fernandes
# drive.py
# Drive -> JSON, shaped per viewer
#
# Reads relationships but never queries — eager loading is the caller's job.


from app.models import ApplicationStatus


def _iso(value):
    return value.isoformat() if value else None


def serialize_drive(drive, viewer_role, applied_drive_ids=None):
    """`applied_drive_ids` is the set of drive ids the calling student already
    has a row for. Passed in rather than looked up here so the whole list costs
    one extra query instead of one per row."""
    data = {
        "id": drive.id,
        "title": drive.title,
        "description": drive.description,
        "jobType": drive.jobType.value if drive.jobType else None,
        "branch": drive.branch.value if drive.branch else None,
        "minCgpa": drive.minCgpa,
        "eligibleYear": drive.eligibleYear,
        "skillsRequired": drive.skillsRequired or [],
        "salary": drive.salary,
        "numOpenings": drive.numOpenings,
        "applicationDeadline": _iso(drive.applicationDeadline),
        "status": drive.status.value,
        "companyName": drive.company.name,
    }

    if viewer_role in ("company", "admin"):
        # Withdrawn applications don't count toward the applicant tally.
        data["applicationCount"] = sum(
            1 for a in drive.applications if a.status != ApplicationStatus.REVOKED
        )

    if viewer_role == "student":
        data["alreadyApplied"] = drive.id in (applied_drive_ids or set())

    return data
