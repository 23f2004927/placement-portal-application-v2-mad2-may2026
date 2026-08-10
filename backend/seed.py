# 4 aug 26 updated
# Christiano Fernandes
# seed.py
# drops/recreates tables and populates dummy data for local testing


from datetime import UTC, datetime, timedelta

from app import create_app
from app.extensions import db
from app.models import (
    Admin,
    Application,
    ApplicationStatus,
    Branch,
    Company,
    Drive,
    DriveStatus,
    JobType,
    Role,
    AccountStatus,
    Student,
    User,
)

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    # --- Admin ---
    admin_user = User(userName="admin", role=Role.ADMIN, accountStatus=AccountStatus.APPROVED, blackListed=False)
    admin_user.setPassword("admin123")
    db.session.add(admin_user)
    db.session.flush()

    admin = Admin(name="Placement Cell", email="admin@institute.edu", userId=admin_user.id)
    db.session.add(admin)

    # --- Students ---
    student_user_1 = User(userName="student1", role=Role.STUDENT, accountStatus=AccountStatus.APPROVED, blackListed=False)
    student_user_1.setPassword("student123")
    db.session.add(student_user_1)
    db.session.flush()

    student1 = Student(
        name="Asha Rao",
        email="asha.rao@example.com",
        phoneNumber="9876543210",
        rollNumber="CS2023001",
        branch=Branch.COMPUTER,
        yearStudy="3rd",
        gradeYear=2027,
        cgpa=8.75,
        links=["linkedin.com/in/asharao", "github.com/asharao"],
        resume="resumes/asha_rao.pdf",
        userId=student_user_1.id,
    )
    db.session.add(student1)

    student_user_2 = User(userName="student2", role=Role.STUDENT, accountStatus=AccountStatus.APPROVED, blackListed=False)
    student_user_2.setPassword("student123")
    db.session.add(student_user_2)
    db.session.flush()

    student2 = Student(
        name="Rohit Mehta",
        email="rohit.mehta@example.com",
        phoneNumber="9123456780",
        rollNumber="EC2023045",
        branch=Branch.ELECTRONICS,
        yearStudy="4th",
        gradeYear=2026,
        cgpa=7.9,
        links=["github.com/rohitm"],
        resume="resumes/rohit_mehta.pdf",
        userId=student_user_2.id,
    )
    db.session.add(student2)

    # --- Companies ---
    company_user_1 = User(userName="techcorp", role=Role.COMPANY, accountStatus=AccountStatus.APPROVED, blackListed=False)
    company_user_1.setPassword("company123")
    db.session.add(company_user_1)
    db.session.flush()

    company1 = Company(
        name="TechCorp Solutions",
        industry="Software",
        location="Bangalore",
        hrContactName="Priya Nair",
        hrContactEmail="priya.nair@techcorp.com",
        website="https://techcorp.example.com",
        userId=company_user_1.id,
    )
    db.session.add(company1)

    company_user_2 = User(userName="buildwell", role=Role.COMPANY, accountStatus=AccountStatus.PENDING, blackListed=False)
    company_user_2.setPassword("company123")
    db.session.add(company_user_2)
    db.session.flush()

    company2 = Company(
        name="BuildWell Infra",
        industry="Construction",
        location="Mumbai",
        hrContactName="Karan Shah",
        hrContactEmail="karan.shah@buildwell.com",
        website="https://buildwell.example.com",
        userId=company_user_2.id,
    )
    db.session.add(company2)
    db.session.flush()

    # --- Drives ---
    drive1 = Drive(
        companyId=company1.id,
        title="Software Engineer",
        description="Entry-level SDE role working on backend systems.",
        branch=Branch.COMPUTER,
        minCgpa=7.5,
        eligibleYear=2027,
        skillsRequired=["Python", "SQL", "Flask"],
        salary=1200000.0,
        numOpenings=5,
        jobType=JobType.FULL_TIME,
        applicationDeadline=datetime.now(UTC) + timedelta(days=14),
        status=DriveStatus.APPROVED,
    )
    db.session.add(drive1)

    drive2 = Drive(
        companyId=company1.id,
        title="Data Analyst Intern",
        description="Summer internship on the analytics team.",
        minCgpa=7.0,
        skillsRequired=["Excel", "SQL", "Python"],
        salary=40000.0,
        numOpenings=3,
        jobType=JobType.INTERNSHIP,
        applicationDeadline=datetime.now(UTC) + timedelta(days=21),
        status=DriveStatus.PENDING,
    )
    db.session.add(drive2)

    # Approved and open — this is the drive the seeded OFFER hangs off, so the
    # accept / decline flow is reachable from a drive the student can also see.
    drive3 = Drive(
        companyId=company1.id,
        title="QA Engineer",
        description="Manual and automated testing for the platform team.",
        minCgpa=6.5,
        skillsRequired=["Python", "Selenium", "SQL"],
        salary=900000.0,
        numOpenings=2,
        jobType=JobType.FULL_TIME,
        applicationDeadline=datetime.now(UTC) + timedelta(days=10),
        status=DriveStatus.APPROVED,
    )
    db.session.add(drive3)
    db.session.flush()

    # --- Applications ---
    application1 = Application(
        studentId=student1.id,
        driveId=drive1.id,
        status=ApplicationStatus.SHORTLISTED,
        interviewScheduledAt=datetime.now(UTC) + timedelta(days=5),
        feedback="Strong technical round, proceeding to HR round.",
    )
    db.session.add(application1)

    application2 = Application(
        studentId=student2.id,
        driveId=drive1.id,
        status=ApplicationStatus.APPLIED,
    )
    db.session.add(application2)

    # An open offer, so the student's accept / decline flow has something to act
    # on the moment the database is seeded.
    application3 = Application(
        studentId=student1.id,
        driveId=drive3.id,
        status=ApplicationStatus.OFFER,
        feedback="Offer extended — please confirm through the portal.",
    )
    db.session.add(application3)

    db.session.commit()

    print("Seed data created at:", app.config["SQLALCHEMY_DATABASE_URI"])
