from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

from app.extensions import db,IntegrityError
from app.models import AccountStatus, Role, Student, User, Branch


auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    # 1. look up by userName
    user = User.query.filter_by(userName=data["userName"]).first()

    if user is None or not user.checkPassword(data["password"]):
        return jsonify(message="Invalid credentials"), 401

    if user.blackListed:
        return jsonify(message="Black Listed account"), 403

    if user.accountStatus != AccountStatus.APPROVED:
        return jsonify(message="Account pending approval"), 403

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role.value, "username": user.userName},
    )

    return jsonify(
        access_token=token, role=user.role.value, userName=user.userName
    ), 200


@auth_bp.route("/register/student", methods=["POST"])
def register_student():

    UNIQUE_ERRORS = {
        "user.userName":       ("userName",    "That username is taken."),
        "student.email":       ("email",       "That email is already registered."),
        "student.rollNumber":  ("rollNumber",  "That roll number is already registered."),
        "student.phoneNumber": ("phoneNumber", "That phone number is already registered."),
        "company.name":        ("name",        "That company is already registered."),
        "company.website":        ("website",        "That website is already registered with a company."),
    }


    data = request.get_json()

    def unique_conflict(exc):
        text = str(exc.orig)
        for constraint, (field, msg) in UNIQUE_ERRORS.items():
            if constraint in text:
                return {field: msg}
        return {}


    user = User(
        userName=data["userName"],
        role=Role.STUDENT,
        accountStatus=AccountStatus.APPROVED,
        blackListed=False,
    )
    user.setPassword(data["password"])
    # expectation: insteadof explicity db querying, we find the errors caused due to unique violations here,
    # any other unmapped error may occur look into it
    try:
        db.session.add(user)
        db.session.flush()
        student = Student(
            userId=user.id,
            name=data["name"],
            email=data["email"],
            phoneNumber=data["phoneNumber"],
            rollNumber=data["rollNumber"],
            branch = Branch(data["branch"]),
            yearStudy=data["yearStudy"],
            gradeYear = int(data["gradeYear"]) if data.get("gradeYear") else None,
            cgpa = float(data["cgpa"]),
        )
        db.session.add(student)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        errors = unique_conflict(e)
        return jsonify(
               message="Some details are already registered.",
               errors=errors,
           ), 409

    return jsonify(message="Registration successful.", userName=user.userName), 201


# {'userName': 'stud1', 'password': 'stud1stud1', 'name': 'stud', 'email': 'stud1@stud1.com', 'phoneNumber': '9049000388',
#    'rollNumber': '23stud1', 'branch': 'computer', 'yearStudy': '1', 'gradeYear': '2027', 'cgpa': '6'}


@auth_bp.route("/register/company", methods=["POST"])
def register_company():

    return jsonify(), 200
