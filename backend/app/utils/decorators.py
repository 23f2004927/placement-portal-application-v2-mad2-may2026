# 7 aug 26
# Christiano Fernandes
# decorators.py
# route guards shared by every blueprint


from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt, jwt_required


def role_required(*roles):
    """Reject anyone whose signed JWT claim isn't in `roles`.

    Three nested functions because the decorator takes arguments: the outer call
    captures `roles`, the middle receives the view, the inner replaces it.

    @wraps is load-bearing, not cosmetic: Flask derives the endpoint name from
    fn.__name__, so without it every decorated view is called "wrapper" and the
    second one registered raises
    "View function mapping is overwriting an existing endpoint function".

    At the call site @route must sit ABOVE @role_required, otherwise Flask
    registers the unwrapped function and the guard never runs.
    """

    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            if get_jwt().get("role") not in roles:
                return jsonify(message="Forbidden"), 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator
