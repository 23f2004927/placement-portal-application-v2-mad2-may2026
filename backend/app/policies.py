# 7 aug 26
# Christiano Fernandes
# policies.py
# who may do what to an application, and in which states
#
# Deliberately Flask-free: no request, no session, no queries. That keeps the
# rules testable without an app context, and stops them quietly growing a
# dependency on the request cycle.
#
# Every function here has exactly two callers — the serializer that ADVERTISES
# the action, and the endpoint that AUTHORISES it. Same constants both times, so
# "button shown" and "request permitted" cannot drift apart.


from app.models import ApplicationStatus, DriveStatus

S = ApplicationStatus
D = DriveStatus

# A student may withdraw only before anyone has committed time to them.
REVOKABLE = {S.APPLIED, S.SHORTLISTED}

# What a company may move an application TO...
COMPANY_SETTABLE = {S.SHORTLISTED, S.INTERVIEW, S.OFFER, S.REJECTED, S.PLACED}

# ...and the states it may move FROM. REVOKED and the terminal states are absent
# on purpose: once a student withdraws or a decision lands, the row is frozen.
COMPANY_SETTABLE_FROM = {S.APPLIED, S.SHORTLISTED, S.INTERVIEW, S.OFFER}

# Companies never see withdrawn applications.
HIDDEN_FROM_COMPANY = {S.REVOKED}


def _values(statuses):
    """Enums aren't JSON-serialisable, and the frontend compares against the
    string it already received in `row.status`."""
    return sorted(s.value for s in statuses)


def capabilities_for(role):
    """The block returned once per list response. Read by useCapabilities()."""
    revoke = {"allowedFrom": _values(REVOKABLE)}
    set_status = {
        "options": _values(COMPANY_SETTABLE),
        "allowedFrom": _values(COMPANY_SETTABLE_FROM),
    }

    if role == "student":
        return {"revoke": revoke}
    if role == "company":
        return {"setStatus": set_status}
    if role == "admin":
        return {"revoke": revoke, "setStatus": set_status}
    return {}


def can_revoke(application, role):
    return role in ("student", "admin") and application.status in REVOKABLE


def can_set_status(application, role, new_status):
    return (
        role in ("company", "admin")
        and new_status in COMPANY_SETTABLE
        and application.status in COMPANY_SETTABLE_FROM
    )


# ---------------------------------------------------------------- drives ----
#
# DriveStatus has no REJECTED member, so admin rejection maps to CLOSED: the
# posting exists, is on record, and no student can apply to it.

# A company may edit a posting until it closes.
DRIVE_EDITABLE = {D.PENDING, D.APPROVED}

# Only a live posting can be taken down.
DRIVE_CLOSABLE = {D.APPROVED}

# Admin moderates once, while it is still awaiting review.
DRIVE_MODERATABLE = {D.PENDING}

# Students only ever see approved postings.
STUDENT_VISIBLE_DRIVES = {D.APPROVED}


def drive_capabilities_for(role):
    if role == "company":
        return {
            "edit": {"allowedFrom": _values(DRIVE_EDITABLE)},
            "close": {"allowedFrom": _values(DRIVE_CLOSABLE)},
        }
    if role == "admin":
        return {
            "approve": {"allowedFrom": _values(DRIVE_MODERATABLE)},
            "reject": {"allowedFrom": _values(DRIVE_MODERATABLE)},
        }
    if role == "student":
        return {"apply": {"allowedFrom": _values(STUDENT_VISIBLE_DRIVES)}}
    return {}


def can_edit_drive(drive, role):
    return role == "company" and drive.status in DRIVE_EDITABLE


def can_close_drive(drive, role):
    return role in ("company", "admin") and drive.status in DRIVE_CLOSABLE


def can_moderate_drive(drive, role):
    return role == "admin" and drive.status in DRIVE_MODERATABLE
