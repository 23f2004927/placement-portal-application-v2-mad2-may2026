# 10 aug 26 rewritten
# Christiano Fernandes
# seed.py
# drops/recreates tables and populates a realistic dataset for local testing
#
# Two things matter here beyond volume:
#
# 1. EVERYTHING IS BACKDATED. appliedAt, statusUpdatedAt and Drive.createdAt are
#    set explicitly rather than left to their server_default, which would stamp
#    every row with "now" and collapse every six-month chart into one bar.
#
# 2. ALL DATETIMES ARE NAIVE LOCAL. The API stores whatever the browser's
#    datetime-local input sends, which is local wall-clock, so the seed matches
#    that. Mixing datetime.now(UTC) in here (as an earlier version did) left two
#    kinds of value in one column, 5.5 hours apart, with nothing marking which
#    was which.
#
# random.seed() is fixed, so re-running produces the same database.


import argparse
import os
import random
import shutil
from datetime import date, datetime, timedelta

from app import create_app
from app.extensions import db
from app.policies import drive_ineligibility
from app.routes.resumes import PDF_MAGIC, resume_dir, stored_name
from app.models import (
    AccountStatus,
    Admin,
    Application,
    ApplicationStatus,
    Branch,
    Company,
    Drive,
    DriveStatus,
    JobType,
    Notification,
    OfferLetter,
    Placement,
    Role,
    Student,
    User,
)

random.seed(7)

# Optional, because the repo carries no PDF: point it at any real one and every
# student gets a copy as their resume, so the company applicant list has
# something to open on a fresh seed.
#   python seed.py --resume ~/Downloads/blank.pdf
parser = argparse.ArgumentParser(description="Populate the local database.")
parser.add_argument("--resume", metavar="PATH", help="PDF to copy in as every student's resume")
args = parser.parse_args()

NOW = datetime.now()
MONTHS_BACK = 6

# Weighted so the funnel narrows the way a real one does, and so every status
# — including the two terminal ones a student causes — is represented.
STATUS_WEIGHTS = [
    (ApplicationStatus.APPLIED, 34),
    (ApplicationStatus.SHORTLISTED, 16),
    (ApplicationStatus.INTERVIEW, 11),
    (ApplicationStatus.OFFER, 6),
    (ApplicationStatus.PLACED, 12),
    (ApplicationStatus.REJECTED, 15),
    (ApplicationStatus.DECLINED, 4),
    (ApplicationStatus.REVOKED, 2),
]

# Real cohorts concentrate in a few branches. Spreading 60 students evenly over
# all 18 leaves ~3 per branch, so any branch-restricted drive has an eligible
# pool of about one person — which made almost every seeded application land
# below its drive's criteria.
BRANCH_WEIGHTS = {
    "COMPUTER": 14,
    "INFORMATION_TECHNOLOGY": 9,
    "ELECTRONICS": 9,
    "MECHANICAL": 8,
    "ELECTRICAL": 6,
    "CIVIL": 5,
    "AI_ML": 5,
    "DATA_SCIENCE": 4,
    "ELECTRONICS_AND_TELECOMMUNICATION": 3,
    "CHEMICAL": 3,
}

FIRST_NAMES = [
    "Asha", "Rohit", "Meera", "Karan", "Priya", "Arjun", "Sneha", "Vikram",
    "Neha", "Aditya", "Divya", "Rahul", "Ananya", "Siddharth", "Kavya",
    "Manish", "Pooja", "Nikhil", "Ritu", "Sameer", "Isha", "Varun", "Tara",
    "Gaurav", "Lakshmi", "Imran", "Farah", "Joseph", "Nandini", "Yash",
]
LAST_NAMES = [
    "Rao", "Mehta", "Iyer", "Shah", "Nair", "Kulkarni", "Banerjee", "Reddy",
    "Chopra", "Desai", "Menon", "Joshi", "Pillai", "Sinha", "Fernandes",
]

COMPANIES = [
    ("TechCorp Solutions", "Software", "Bangalore", "techcorp"),
    ("BuildWell Infra", "Construction", "Mumbai", "buildwell"),
    ("Northwind Analytics", "Analytics", "Pune", "northwind"),
    ("Vertex Motors", "Automotive", "Chennai", "vertex"),
    ("Cobalt Energy", "Energy", "Ahmedabad", "cobalt"),
    ("Lumen Health", "Healthcare", "Hyderabad", "lumen"),
    ("Ardent Robotics", "Robotics", "Bangalore", "ardent"),
    ("Quill Financial", "Finance", "Mumbai", "quill"),
    ("Beacon Aerospace", "Aerospace", "Bangalore", "beacon"),
    ("Ridge Consulting", "Consulting", "Gurgaon", "ridge"),
    ("Halcyon Media", "Media", "Mumbai", "halcyon"),
    ("Strand Biotech", "Biotech", "Hyderabad", "strand"),
]

# A student's own skills are drawn from the same vocabulary the drives use, so
# the ATS screener and the skill search have something real to match against.
BENEFITS = [
    "Health insurance, annual learning budget, hybrid working.",
    "Relocation support, subsidised meals, quarterly bonus.",
    "Health cover for family, paid certifications, flexible hours.",
    "Stock options after 12 months, gym reimbursement, 24 days leave.",
    None,
]

EXPERIENCE_ASKED = ["Fresher", "0–1 years", "0–2 years", "1–3 years", None]

EXPERIENCE_HAD = [
    "Summer internship at a product startup; built and shipped two internal tools.",
    "Two semester-long projects and a 3-month remote internship.",
    "Final-year capstone plus freelance work for a local business.",
    "Teaching assistant for two courses; several open-source contributions.",
    None,
]

ROLES = [
    ("Software Engineer", ["Python", "SQL", "Git"]),
    ("Backend Developer", ["Python", "Flask", "PostgreSQL", "REST"]),
    ("Frontend Developer", ["JavaScript", "Vue", "CSS", "HTML"]),
    ("Data Analyst", ["SQL", "Excel", "Python", "Tableau"]),
    ("Data Scientist", ["Python", "Machine Learning", "Statistics", "SQL"]),
    ("QA Engineer", ["Selenium", "Python", "Testing"]),
    ("DevOps Engineer", ["Docker", "Linux", "AWS", "CI"]),
    ("Mechanical Design Engineer", ["CAD", "SolidWorks", "GD&T"]),
    ("Site Engineer", ["AutoCAD", "Project Management", "Surveying"]),
    ("Electrical Engineer", ["Circuit Design", "MATLAB", "PLC"]),
    ("Embedded Engineer", ["C", "Microcontrollers", "RTOS"]),
    ("Business Analyst", ["Excel", "SQL", "Communication"]),
    ("Process Engineer", ["Chemical Processes", "Safety", "Excel"]),
    ("Research Associate", ["Lab Techniques", "Statistics", "Reporting"]),
]

# Every skill any drive asks for, so a student's own list overlaps meaningfully.
ALL_SKILLS = sorted({skill for _, skills in ROLES for skill in skills})


def past(days_min, days_max):
    """A naive local datetime somewhere in the given window before now."""
    delta = timedelta(
        days=random.randint(days_min, days_max),
        hours=random.randint(0, 23),
        minutes=random.choice([0, 15, 30, 45]),
    )
    return NOW - delta


def weighted_status():
    population = [s for s, _ in STATUS_WEIGHTS]
    weights = [w for _, w in STATUS_WEIGHTS]
    return random.choices(population, weights=weights, k=1)[0]


def make_user(username, role, password, status=AccountStatus.APPROVED, blacklisted=False):
    user = User(userName=username, role=role, accountStatus=status, blackListed=blacklisted)
    user.setPassword(password)
    db.session.add(user)
    return user


def check_resume_source(path):
    """Fail before writing 60 copies of something that isn't a PDF."""
    if not os.path.isfile(path):
        raise SystemExit(f"--resume: no such file: {path}")
    with open(path, "rb") as handle:
        if handle.read(len(PDF_MAGIC)) != PDF_MAGIC:
            raise SystemExit(f"--resume: not a PDF: {path}")


app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    # drop_all() clears the tables but not the disk, so PDFs from an earlier run
    # would outlive the students they belonged to.
    shutil.rmtree(resume_dir(), ignore_errors=True)

    resume_source = os.path.expanduser(args.resume) if args.resume else None
    if resume_source:
        check_resume_source(resume_source)

    # ---------------------------------------------------------------- admin --
    admin_user = make_user("admin", Role.ADMIN, "admin123")
    db.session.flush()
    db.session.add(Admin(name="Placement Cell", email="admin@institute.edu", userId=admin_user.id))

    # ------------------------------------------------------------ companies --
    # Index 1 (BuildWell) stays PENDING and index 11 is REJECTED, so account
    # moderation and the "pending company can read but not write" gate both
    # have something to act on immediately.
    companies = []
    for i, (name, industry, location, handle) in enumerate(COMPANIES):
        if i == 1:
            account = AccountStatus.PENDING
        elif i == 11:
            account = AccountStatus.REJECTED
        else:
            account = AccountStatus.APPROVED

        user = make_user(handle, Role.COMPANY, "company123", status=account)
        db.session.flush()

        company = Company(
            name=name,
            industry=industry,
            location=location,
            hrContactName=f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
            hrContactEmail=f"hr@{handle}.example.com",
            website=f"https://{handle}.example.com",
            userId=user.id,
        )
        db.session.add(company)
        companies.append(company)

    db.session.flush()
    hiring = [c for c in companies if c.user.accountStatus is AccountStatus.APPROVED]

    # ------------------------------------------------------------- students --
    branches = list(Branch)
    branch_weights = [BRANCH_WEIGHTS.get(b.name, 1) for b in branches]

    students = []
    for i in range(1, 61):
        branch = random.choices(branches, weights=branch_weights, k=1)[0]
        first, last = random.choice(FIRST_NAMES), random.choice(LAST_NAMES)

        # student1 is blacklisted-free and approved like the rest; index 59 is
        # blacklisted so the admin restore flow has a subject.
        user = make_user(f"student{i}", Role.STUDENT, "student123", blacklisted=(i == 59))
        db.session.flush()

        student = Student(
            name=f"{first} {last}",
            email=f"{first.lower()}.{last.lower()}{i}@student.institute.edu",
            phoneNumber=f"90000000{i:02d}",
            rollNumber=f"23{branch.name[:3]}{i:03d}",
            branch=branch,
            yearStudy=str(random.choice([3, 4])),
            gradeYear=random.choice([2026, 2027, 2028]),
            cgpa=round(random.uniform(5.2, 9.8), 2),
            links={"github": f"https://github.com/student{i}"} if i % 3 == 0 else None,
            skills=random.sample(ALL_SKILLS, random.randint(3, 7)),
            experience=random.choice(EXPERIENCE_HAD),
            userId=user.id,
        )
        db.session.add(student)
        students.append(student)

    db.session.flush()

    # Needs the flush above: the filename is derived from student.id. Without
    # --resume every student is left with no resume, which is also a valid state
    # to test — the company's button greys out.
    if resume_source:
        for student in students:
            shutil.copyfile(resume_source, os.path.join(resume_dir(), stored_name(student.id)))
            student.resume = stored_name(student.id)
            student.resumeUploadedAt = past(1, 90)

    # --------------------------------------------------------------- drives --
    # Spread across the whole window so the monthly and cumulative charts have
    # a shape rather than a single spike.
    drives = []
    for i in range(36):
        company = random.choice(hiring)
        title, skills = random.choice(ROLES)
        created = past(3, MONTHS_BACK * 30)

        # Most are approved; a few await moderation, a few have closed.
        status = random.choices(
            [DriveStatus.APPROVED, DriveStatus.PENDING, DriveStatus.CLOSED],
            weights=[70, 15, 15],
            k=1,
        )[0]

        job_type = random.choices(
            [JobType.FULL_TIME, JobType.INTERNSHIP, JobType.PPO], weights=[60, 30, 10], k=1
        )[0]

        salary = (
            round(random.uniform(6, 24)) * 100000
            if job_type is JobType.FULL_TIME
            else round(random.uniform(15, 60)) * 1000
        )

        drives.append(
            Drive(
                companyId=company.id,
                title=title,
                description=f"{title} opening at {company.name}.",
                # Two thirds are open to any branch — the eligibility annotation
                # is only interesting when some drives restrict and some don't.
                # Weighted the same way as the cohort, so a restricted drive
                # still has real candidates to draw from.
                # Criteria COMPOUND, and they are now enforced rather than
                # advisory: a drive restricting all three axes at once is one
                # almost nobody can apply to. Each is therefore unset most of
                # the time, which leaves every student a real shortlist.
                branch=random.choices(branches, weights=branch_weights, k=1)[0]
                if random.random() < 0.25
                else None,
                minCgpa=random.choices(
                    [None, 6.0, 6.5, 7.0, 7.5], weights=[40, 15, 15, 15, 15], k=1
                )[0],
                eligibleYear=random.choices([None, 2026, 2027], weights=[55, 25, 20], k=1)[0],
                skillsRequired=random.sample(skills, k=min(len(skills), random.randint(2, 4))),
                experienceRequired=random.choice(EXPERIENCE_ASKED),
                salary=salary,
                benefits=random.choice(BENEFITS),
                numOpenings=random.randint(1, 8),
                jobType=job_type,
                # Weighted toward the future so there is a browsable set of open
                # drives; the expired ones keep "closed" reachable.
                applicationDeadline=NOW
                + timedelta(days=random.choice([*range(-40, 0), *range(1, 61), *range(1, 61)])),
                status=status,
                createdAt=created,
                updatedAt=created,
            )
        )

    db.session.add_all(drives)
    db.session.flush()

    # ---------------------------------------------------------- applications --
    seen = set()   # (studentId, driveId) — the model's unique constraint
    applications = []

    # Who actually qualifies for what, worked out once (36 x 60 checks).
    # Drawing a student at random and rejecting the misfits would throw away
    # most pairs, because eligible pairs are the minority — so pick the drive
    # first and then draw from its own pool.
    eligible_for = {
        drive.id: [s for s in students if not drive_ineligibility(drive, s)] for drive in drives
    }

    # More attempts than before: now that only eligible pairs are allowed, each
    # draw comes from a smaller pool and collides with an existing pair sooner.
    for _ in range(900):
        drive = random.choice(drives)
        pool = eligible_for[drive.id]

        # Only eligible students, because that is now the only way an
        # application can be created — POST /api/applications rejects the rest.
        # `belowCriteria` on the company's list is still reachable in real use:
        # a company that TIGHTENS its criteria after applications arrive.
        if not pool:
            continue
        student = random.choice(pool)

        key = (student.id, drive.id)
        if key in seen:
            continue
        seen.add(key)

        applied = drive.createdAt + timedelta(days=random.randint(0, 20))
        if applied > NOW:
            continue

        status = weighted_status()
        # The last change is always at or after the application, never ahead of
        # now — a future timestamp would break every month-bucketed chart.
        updated = min(applied + timedelta(days=random.randint(1, 35)), NOW)

        application = Application(
            studentId=student.id,
            driveId=drive.id,
            status=status,
            appliedAt=applied,
            statusUpdatedAt=updated,
        )

        if status is ApplicationStatus.INTERVIEW:
            # Some upcoming (so "interviews this week" is non-zero), some past.
            application.interviewScheduledAt = NOW + timedelta(
                days=random.randint(-10, 12), hours=random.randint(9, 17)
            )

        if status in (ApplicationStatus.REJECTED, ApplicationStatus.OFFER, ApplicationStatus.PLACED):
            application.feedback = random.choice(
                [
                    "Strong fundamentals, good communication.",
                    "Technical round cleared; proceeding.",
                    "Not a fit for this role at present.",
                    "Impressive project work.",
                    "Offer extended — please confirm through the portal.",
                ]
            )

        if status is ApplicationStatus.PLACED:
            application.finalSalary = drive.salary
            application.joiningDate = (updated + timedelta(days=random.randint(30, 120))).date()

        applications.append(application)

    db.session.add_all(applications)
    db.session.flush()

    # --------------------------------------------------------- offer letters --
    # Most placements have paperwork; a few deliberately do not, so the "issue
    # after acceptance" path is reachable.
    for application in applications:
        if application.status is ApplicationStatus.PLACED and random.random() < 0.8:
            drive = application.drive
            db.session.add(
                OfferLetter(
                    applicationId=application.id,
                    roleTitle=drive.title,
                    companyName=drive.company.name,
                    jobType=drive.jobType.value if drive.jobType else None,
                    location=drive.company.location,
                    salary=drive.salary,
                    joiningDate=application.joiningDate,
                    issuedAt=application.statusUpdatedAt,
                )
            )

    # ------------------------------------------------------------ placements --
    # One per accepted offer, exactly as POST /applications/<id>/respond writes
    # it. Seeding the status without the register would leave the two disagreeing.
    for application in applications:
        if application.status is ApplicationStatus.PLACED:
            drive = application.drive
            db.session.add(
                Placement(
                    studentId=application.studentId,
                    companyId=drive.companyId,
                    applicationId=application.id,
                    position=drive.title,
                    salary=application.finalSalary,
                    joiningDate=application.joiningDate,
                    placedAt=application.statusUpdatedAt,
                )
            )

    # --------------------------------------------------------- notifications --
    # A few unread, so the topbar bell has a count before any Celery job runs.
    db.session.add(
        Notification(
            userId=admin_user.id,
            title="Placement report — last month",
            body="Generated by the monthly reporting job.",
            createdAt=past(1, 20),
        )
    )
    for student in random.sample(students, 6):
        db.session.add(
            Notification(
                userId=student.user.id,
                title=random.choice(["Interview tomorrow", "Drive closing soon"]),
                body="Open your applications to see the details.",
                createdAt=past(0, 5),
            )
        )

    db.session.commit()

    # ------------------------------------------------------------- summary ---
    placed = sum(1 for a in applications if a.status is ApplicationStatus.PLACED)
    print("Seeded:", app.config["SQLALCHEMY_DATABASE_URI"])
    print(f"  companies     {len(companies)}  ({len(hiring)} approved, 1 pending, 1 rejected)")
    print(f"  students      {len(students)}  (student59 blacklisted)")
    print(f"  drives        {len(drives)}  spread over the last {MONTHS_BACK} months")
    print(f"  applications  {len(applications)}  ({placed} placed)")
    print(f"  resumes       {len(students) if resume_source else 0}  (pass --resume PATH to attach one)")
    print()
    print("  admin / admin123      company handles / company123      student1..60 / student123")
