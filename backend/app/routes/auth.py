from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required

from app.extensions import db,IntegrityError
from app.utils.errors import unique_conflict
from app.models import AccountStatus, Role, Student, User, Branch,Company
from app.utils.identity import current_user_id



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

    if user.accountStatus == AccountStatus.REJECTED:
        return jsonify(message="Account rejected"), 403

    # PENDING is deliberately allowed through: a company awaiting review may sign
    # in and look around. What it may not do is write — see role_required(approved=True).
    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role.value, "username": user.userName},
    )

    # accountStatus rides along so the SPA can gate its UI with no second request.
    # A hint only: it is NOT a token claim, and every write re-reads the live row.
    return jsonify(
        access_token=token,
        role=user.role.value,
        userName=user.userName,
        accountStatus=user.accountStatus.value,
    ), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """Refreshes what the SPA cached at login.

    Needed because JWT claims are frozen at issue time: a company approved
    mid-session would otherwise keep seeing the restricted UI until it logged
    out. Called once per dashboard mount, not once per navigation.
    """
    user = db.session.get(User, current_user_id())
    if user is None:
        return jsonify(message="Account no longer exists."), 404

    return jsonify(
        userName=user.userName,
        role=user.role.value,
        accountStatus=user.accountStatus.value,
        blackListed=user.blackListed,
    ), 200


@auth_bp.route("/register/student", methods=["POST"])
def register_student():

    data = request.get_json()

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

    data = request.get_json()

    user = User(
        userName=data["userName"],
        role=Role.COMPANY,
        accountStatus=AccountStatus.PENDING,
        blackListed=False,
    )
    user.setPassword(data["password"])
    # expectation: insteadof explicity db querying, we find the errors caused due to unique violations here,
    # any other unmapped error may occur look into it
    try:
        db.session.add(user)
        db.session.flush()
        company = Company(
            userId=user.id,
            name=data["name"],
            industry = data["industry"],
            location = data["location"] if data.get("location") else None,
            hrContactEmail=data["hrContactEmail"],
            hrContactName=data["hrContactName"],
            website=data["website"],
        )
        db.session.add(company)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        errors = unique_conflict(e)
        return jsonify(
               message="Some details are already registered.",
               errors=errors,
           ), 409

    return jsonify(message="Registration successful.", userName=user.userName), 201
