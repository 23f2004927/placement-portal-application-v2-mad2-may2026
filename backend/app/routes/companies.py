# 8 aug 26
# Christiano Fernandes
# companies.py
# /api/admin/companies — company account moderation
# /api/companies       — the read-only recruiter directory students see
#
# Two endpoints rather than one branching on role, because they are not the
# same resource narrowed: the admin's list is an account register with a
# moderation queue, the student's is a directory of who recruits here. Sharing
# a route would mean one payload builder deciding, per field, who may see it.
#
# Scoped to companies rather than a generic /api/admin/users endpoint on purpose:
# a generic one could blacklist the admin account and lock everyone out.


from flask import Blueprint, jsonify, request
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models import AccountStatus, Company, Drive, DriveStatus, User
from app.policies import account_capabilities_for, can_blacklist, can_moderate_account
from app.serializers import serialize_company
from app.utils.caching import cached_payload, invalidate, scoped_key
from app.utils.decorators import role_required
from app.utils.pagination import enum_filter, paginate, search, sort


companies_bp = Blueprint("companies", __name__, url_prefix="/api")



@companies_bp.route("/admin/companies", methods=["GET"])
@role_required("admin")
def list_companies():
    # joinedload is load-bearing: the serializer reads company.user for three
    # fields, so without it every row costs an extra SELECT.
    # per_user=False: every admin sees exactly the same register, so one shared
    # key is correct here — unlike /api/drives, nothing is scoped to the caller.
    def build():
        query = Company.query.options(joinedload(Company.user)).join(
            User, Company.userId == User.id
        )
        query = search(
            query, [Company.name, Company.industry, Company.location, Company.hrContactEmail]
        )
        query = enum_filter(query, User.accountStatus, AccountStatus)
        query = sort(
            query,
            {
                "name": Company.name,
                "industry": Company.industry,
                "location": Company.location,
                "hrContactEmail": Company.hrContactEmail,
                "accountStatus": User.accountStatus,
            },
            default=(Company.name, Company.id),
        )

        companies, meta = paginate(query)
        return {
            "items": [serialize_company(c, "admin") for c in companies],
            "capabilities": account_capabilities_for("admin"),
            **meta,
        }

    return jsonify(cached_payload(scoped_key("companies", per_user=False), build)), 200


@companies_bp.route("/companies", methods=["GET"])
@role_required("student")
def list_companies_for_students():
    """The recruiter directory. Approved and non-blacklisted only — a student
    has no business seeing an account the admin turned down, and a rejected
    company appearing here would read as an endorsement.

    Each row carries how many drives the company currently has open, which is
    the one number that makes the list worth browsing.
    """

    def build():
        open_drives = (
            db.session.query(Drive.companyId, db.func.count(Drive.id).label("openDrives"))
            .filter(Drive.status == DriveStatus.APPROVED)
            .group_by(Drive.companyId)
            .subquery()
        )

        query = (
            Company.query.options(joinedload(Company.user))
            .join(User, Company.userId == User.id)
            .outerjoin(open_drives, open_drives.c.companyId == Company.id)
            .filter(User.accountStatus == AccountStatus.APPROVED, User.blackListed.is_(False))
            .add_columns(db.func.coalesce(open_drives.c.openDrives, 0).label("openDrives"))
        )

        query = search(query, [Company.name, Company.industry, Company.location])
        query = sort(
            query,
            {
                "name": Company.name,
                "industry": Company.industry,
                "location": Company.location,
                "openDrives": db.func.coalesce(open_drives.c.openDrives, 0),
            },
            default=(Company.name, Company.id),
        )

        rows, meta = paginate(query)
        return {
            "items": [
                {**serialize_company(company, "student"), "openDrives": count}
                for company, count in rows
            ],
            # Nothing to do here — the directory is read-only.
            "capabilities": {},
            **meta,
        }

    # Same namespace as the admin register, so approving or blacklisting a
    # company drops both at once — that is the change that MUST be immediate.
    # openDrives depends on the drives namespace instead, so it rides the 60s
    # TTL: a directory count one minute behind is not worth cross-invalidating.
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
