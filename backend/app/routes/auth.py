from app.models import AccountStatus, User
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    # 1. look up by userName
    user = User.query.filter_by(userName=data["userName"]).first()

    if user is None or not user.checkPassword(data["password"]):
        return  jsonify(message="Invalid credentials"), 401

    if user.blackListed:
        return  jsonify(message="Black Listed account"), 403

    if user.accountStatus != AccountStatus.APPROVED:
        return jsonify(message="Account pending approval"), 403

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role.value,"username": user.userName}
    )


    return jsonify(access_token=token,  role=user.role.value, userName=user.userName), 200


    # 2. if not found OR not user.checkPassword(data["password"]) -> 401
    #    (same generic message for both — don't leak which usernames exist)
    # 3. if user.blackListed -> 403
    # 4. if user.accountStatus != AccountStatus.APPROVED -> 403
    # 5. token = create_access_token(
    #        identity=str(user.id),
    #        additional_claims={"role": user.role.value}   # .value! Enum isn't JSON-serializable
    #    )
    # 6. return jsonify(access_token=token, role=user.role.value)
