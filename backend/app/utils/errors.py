# 7 aug 26
# Christiano Fernandes
# errors.py
# maps DB constraint violations to per-field messages
#
# Lives here rather than in auth.py because registration is no longer the only
# place that hits a unique constraint — profile edits do too.


UNIQUE_ERRORS = {
    "user.userName": ("userName", "That username is taken."),
    "student.email": ("email", "That email is already registered."),
    "student.rollNumber": ("rollNumber", "That roll number is already registered."),
    "student.phoneNumber": ("phoneNumber", "That phone number is already registered."),
    "company.name": ("name", "That company is already registered."),
    "company.website": ("website", "That website is already registered with a company."),
    "company.hrContactEmail": ("hrContactEmail", "That contact email is already registered."),
}


def unique_conflict(exc):
    """Turn an IntegrityError into {field: message}.

    SQLite aborts at the FIRST violated constraint, so this reports one error per
    round trip. The wording is also SQLite-specific ('UNIQUE constraint failed:
    table.column') — Postgres phrases it differently.
    """
    text = str(exc.orig)
    for constraint, (field, message) in UNIQUE_ERRORS.items():
        if constraint in text:
            return {field: message}
    return {}
