# 8 aug 26
# Christiano Fernandes
# companies.py
# /api/admin/companies — company account moderation
#
# Unlike /api/applications and /api/drives this is NOT one resource seen three
# ways. It has exactly one audience, so role_required IS the authorization and
# there is no role branch to write.
#
# Scoped to companies rather than a generic /api/admin/users endpoint on purpose:
# a generic one could blacklist the admin account and lock everyone out.


from flask import Blueprint, jsonify, request
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models import AccountStatus, Company
from app.policies import account_capabilities_for, can_blacklist, can_moderate_account
from app.serializers import serialize_company
from app.utils.caching import cached_payload, invalidate, scoped_key
from app.utils.decorators import role_required


companies_bp = Blueprint("companies", __name__, url_prefix="/api")



@companies_bp.route("/admin/companies", methods=["GET"])
@role_required("admin")
def list_companies():
    # joinedload is load-bearing: the serializer reads company.user for three
    # fields, so without it every row costs an extra SELECT.
    # per_user=False: every admin sees exactly the same register, so one shared
    # key is correct here — unlike /api/drives, nothing is scoped to the caller.
    def build():
        companies = (
            Company.query.options(joinedload(Company.user))
            .order_by(Company.name)
            .all()
        )
        return {
            "items": [serialize_company(c, "admin") for c in companies],
            "capabilities": account_capabilities_for("admin"),
        }

    return jsonify(cached_payload(scoped_key("companies", per_user=False), build)), 200


@companies_bp.route("/admin/companies/<int:company_id>", methods=["PATCH"])
@role_required("admin")
def moderate_company(company_id):
    company = db.session.get(Company, company_id)
    if company is None:
        return jsonify(message="Company not found."), 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(message="Invalid request body."), 400

    # Status and blacklist both live on User; Company is only how the admin
    # found the row.
    user = company.user

    if "accountStatus" in data:
        try:
            new_status = AccountStatus(data["accountStatus"])
        except ValueError:
            return jsonify(message="Unknown account status."), 400

        if not can_moderate_account(user, "admin", new_status):
            return jsonify(message="This account has already been reviewed."), 409

        user.accountStatus = new_status

    if "blackListed" in data:
        value = data["blackListed"]

        if not isinstance(value, bool):
            return jsonify(message="blackListed must be true or false."), 400

        if not can_blacklist(user, "admin"):
            return jsonify(message="This account cannot be blacklisted."), 403

        user.blackListed = value

    db.session.commit()
    invalidate("companies")

    return jsonify(serialize_company(company, "admin")), 200
