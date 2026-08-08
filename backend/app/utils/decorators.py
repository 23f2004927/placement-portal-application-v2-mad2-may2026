# 7 aug 26
# Christiano Fernandes
# decorators.py
# route guards shared by every blueprint


from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt, jwt_required

from app.extensions import db
from app.models import AccountStatus, User
from app.utils.identity import current_user_id


def role_required(*roles, approved=False):
    """Reject anyone whose signed JWT claim isn't in `roles`.

    Three nested functions because the decorator takes arguments: the outer call
    captures `roles`, the middle receives the view, the inner replaces it.

    @wraps is load-bearing, not cosmetic: Flask derives the endpoint name from
    fn.__name__, so without it every decorated view is called "wrapper" and the
    second one registered raises
    "View function mapping is overwriting an existing endpoint function".

    At the call site @route must sit ABOVE @role_required, otherwise Flask
    registers the unwrapped function and the guard never runs.

    `approved=True` additionally requires the account to have cleared admin
    review. It defaults to False so read endpoints stay open to a pending
    company — it may look around, it just may not write.
    """

    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            if get_jwt().get("role") not in roles:
                return jsonify(message="Forbidden"), 403

            # Read live from the DB rather than from a claim: an admin approving
            # an account cannot retroactively change a token already issued, so a
            # claim would leave the company locked out until it logged in again.
            #
            # Since the row is loaded anyway, blackListed is checked here too —
            # that makes a blacklist take effect on writes immediately, rather
            # than only at the blacklisted account's next login attempt.
            if approved:
                user = db.session.get(User, current_user_id())
                if user is None or user.blackListed:
                    return jsonify(message="This account is blacklisted."), 403
                if user.accountStatus is not AccountStatus.APPROVED:
                    return jsonify(message="Your account is awaiting approval."), 403

            return fn(*args, **kwargs)

        return wrapper

    return decorator
