# 7 aug 26
# Christiano Fernandes
# profile.py
# Student / Company -> JSON for the profile screens


def serialize_student(student):
    return {
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
        "resume": student.resume,
        "userName": student.user.userName,
        "accountStatus": student.user.accountStatus.value,
    }


def serialize_company(company):
    return {
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
