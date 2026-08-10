# 10 aug 26
# Christiano Fernandes
# validation.py
# request-body validation for the public endpoints
#
# The browser form is not validation, it is UX. HTML5 `required` rejects "" but
# accepts "   ", and any non-browser client skips the form entirely — so before
# this existed, a missing key raised KeyError and returned a 500 with an HTML
# body the SPA could not read.
#
# Errors come back keyed by field, the same shape utils/errors.py produces for
# unique-constraint conflicts, so the frontend renders both the same way.


import re

EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE = re.compile(r"^\d{10}$")

MIN_PASSWORD = 8


def _clean(value):
    """Trim strings; leave everything else alone. A space-only string becomes
    "" here, which the required check below then rejects — that is the whole
    point, since "   " satisfies NOT NULL but breaks a unique index later."""
    return value.strip() if isinstance(value, str) else value


def clean_payload(data, required=(), optional=()):
    """Returns (values, errors). `errors` empty means the payload is usable."""
    if not isinstance(data, dict):
        return {}, {"_": "Invalid request body."}

    values, errors = {}, {}

    for field in required:
        value = _clean(data.get(field))
        if value is None or value == "":
            errors[field] = "This field is required."
        else:
            values[field] = value

    for field in optional:
        value = _clean(data.get(field))
        values[field] = value if value not in (None, "") else None

    return values, errors


def check_email(values, errors, *fields):
    for field in fields:
        value = values.get(field)
        if value and not EMAIL.match(value):
            errors[field] = "Enter a valid email address."


def check_phone(values, errors, *fields):
    for field in fields:
        value = values.get(field)
        if value and not PHONE.match(value):
            errors[field] = "Enter a 10 digit phone number."


def check_password(values, errors, field="password"):
    value = values.get(field)
    if value and len(value) < MIN_PASSWORD:
        errors[field] = f"Use at least {MIN_PASSWORD} characters."


def check_number(values, errors, field, cast=float, low=None, high=None):
    """Coerces in place, so the caller gets a number rather than a string."""
    raw = values.get(field)
    if raw is None:
        return
    try:
        number = cast(raw)
    except (TypeError, ValueError):
        errors[field] = "Enter a number."
        return
    if (low is not None and number < low) or (high is not None and number > high):
        errors[field] = f"Must be between {low} and {high}."
        return
    values[field] = number
