# 7 aug 26
# Christiano Fernandes
# profile.py
# Student / Company -> JSON for the profile screens


def _iso(value):
    return value.isoformat() if value else None


def serialize_student(student,viewer_role):
    data=  {
        "id": student.id,
        "name": student.name,
        "email": student.email,
        "phoneNumber": student.phoneNumber,
        "rollNumber": student.rollNumber,
        "branch": student.branch.value if student.branch else None,
        "yearStudy": student.yearStudy,
        "gradeYear": student.gradeYear,
        "cgpa": student.cgpa,
        "links": student.links or {},
        "skills": student.skills or [],
        "experience": student.experience,
        # Presence only. The filename is never sent — the file is reachable
        # through /api/students/<id>/resume or not at all.
        "resumeUploadedAt": _iso(student.resumeUploadedAt),
        "userName": student.user.userName,
        "accountStatus": student.user.accountStatus.value,
    }
    if viewer_role == "admin":
            data["blackListed"] = student.user.blackListed

    return data


def serialize_company(company,viewer_role):
    data = {
        "id": company.id,
        "name": company.name,
        "industry": company.industry,
        "location": company.location,
        "hrContactName": company.hrContactName,
        "hrContactEmail": company.hrContactEmail,
        "website": company.website,
        "userName": company.user.userName,
        "accountStatus": company.user.accountStatus.value,
    }
    if viewer_role == "admin":
            data["blackListed"] = company.user.blackListed

    return data
