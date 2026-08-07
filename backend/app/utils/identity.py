# 7 aug 26
# Christiano Fernandes
# identity.py
# resolves the JWT identity to the caller's profile row


from flask_jwt_extended import get_jwt, get_jwt_identity

from app.models import Company, Student


def current_user_id():
    return int(get_jwt_identity())


def current_role():
    return get_jwt().get("role")


def current_student():

    return Student.query.filter_by(userId=current_user_id()).first()


def current_company():
    return Company.query.filter_by(userId=current_user_id()).first()
