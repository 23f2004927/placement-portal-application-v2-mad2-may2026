# 7 aug 26
# Christiano Fernandes
# policies.py
# who may do what to an application, a drive or an account, and in which states
#
# Deliberately Flask-free: no request, no session, no queries. That keeps the
# rules testable without an app context, and stops them quietly growing a
# dependency on the request cycle.
#
# Every function here has exactly two callers — the serializer that ADVERTISES
# the action, and the endpoint that AUTHORISES it. Same constants both times, so
# "button shown" and "request permitted" cannot drift apart.


from app.models import AccountStatus, ApplicationStatus, DriveStatus, Role

S = ApplicationStatus
D = DriveStatus

# A student may withdraw only before anyone has committed time to them.
REVOKABLE = {S.APPLIED, S.SHORTLISTED}

# What a company may move an application TO. PLACED is deliberately ABSENT: a
# placement means the student accepted, and only the student can say that.
COMPANY_SETTABLE = {S.SHORTLISTED, S.INTERVIEW, S.OFFER, S.REJECTED}

# ...and the states it may move FROM. REVOKED and the terminal states are absent
# on purpose: once a student withdraws or a decision lands, the row is frozen.
COMPANY_SETTABLE_FROM = {S.APPLIED, S.SHORTLISTED, S.INTERVIEW, S.OFFER}

# Companies never see withdrawn applications. DECLINED is NOT hidden — a student
# turning an offer down is information the company needs.
HIDDEN_FROM_COMPANY = {S.REVOKED}

# The student's side of an offer: accept it, or turn it down.
OFFER_RESPONDABLE = {S.OFFER}
STUDENT_OFFER_DECISIONS = {S.PLACED, S.DECLINED}

# PLACED is included so a company that forgot to issue the letter before the
# student accepted is not locked out of issuing it afterwards.
OFFER_LETTER_ISSUABLE = {S.OFFER, S.PLACED}



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

    issue_offer_letter = {"allowedFrom": _values(OFFER_LETTER_ISSUABLE)}
    respond_to_offer = {
        "options": _values(STUDENT_OFFER_DECISIONS),
        "allowedFrom": _values(OFFER_RESPONDABLE),
    }

    if role == "student":
        return {"revoke": revoke, "respondToOffer": respond_to_offer}
    if role == "company":
        return {"setStatus": set_status, "issueOfferLetter": issue_offer_letter}
    if role == "admin":
        return {
            "revoke": revoke,
            "setStatus": set_status,
            "issueOfferLetter": issue_offer_letter,
            "respondToOffer": respond_to_offer,
        }
    return {}


def can_revoke(application, role):
    return role in ("student", "admin") and application.status in REVOKABLE


def can_respond_to_offer(application, role, new_status):
    """Accepting or declining is the student's own call — a company cannot mark
    someone placed on their behalf, which is why PLACED left COMPANY_SETTABLE."""
    return (
        role in ("student", "admin")
        and new_status in STUDENT_OFFER_DECISIONS
        and application.status in OFFER_RESPONDABLE
    )


def can_issue_offer_letter(application, role):
    return role in ("company", "admin") and application.status in OFFER_LETTER_ISSUABLE


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


def drive_ineligibility(drive, student):
    """Why this student falls outside the drive's criteria.

    Empty list means they meet everything, and only then may they apply.

    Two callers, as everywhere else in this module: the drive serializer, which
    ADVERTISES the reasons so the student is told before clicking, and
    POST /api/applications, which ENFORCES them. One function, so the badge on
    the row and the 403 from the endpoint can never disagree.

    The drive is still listed either way — hiding it would leave the student
    unable to see what they would need to qualify.

    A NULL criterion means no restriction on that axis.
    """
    reasons = []

    if drive.branch is not None and student.branch != drive.branch:
        reasons.append(f"Open to {drive.branch.value.replace('_', ' ')}")

    if drive.minCgpa is not None and (student.cgpa is None or student.cgpa < drive.minCgpa):
        reasons.append(f"Minimum CGPA {drive.minCgpa}")

    if drive.eligibleYear is not None and student.gradeYear != drive.eligibleYear:
        reasons.append(f"Graduating {drive.eligibleYear}")

    return reasons


# -------------------------------------------------------------- accounts ----
#
# Only companies register as PENDING; students are APPROVED on creation. So in
# practice this moderates companies, but it is written against User so a future
# student-approval flow reuses it unchanged.

# A decision is made once, while the account is still awaiting review.
ACCOUNT_MODERATABLE = {AccountStatus.PENDING}

# What an admin may move an account TO. PENDING is absent: you cannot un-review.
ACCOUNT_DECISIONS = {AccountStatus.APPROVED, AccountStatus.REJECTED}

# Blacklisting is orthogonal to accountStatus — a toggle, valid from any status.
ALL_ACCOUNT_STATUSES = set(AccountStatus)


def account_capabilities_for(role, review=True):
    """review=False for students: they register APPROVED, so there is nothing to
    review — only the blacklist lever applies."""
    if role != "admin":
        return {}

    capabilities = {"blacklist": {"allowedFrom": _values(ALL_ACCOUNT_STATUSES)}}
    if review:
        capabilities["setAccountStatus"] = {
            "options": _values(ACCOUNT_DECISIONS),
            "allowedFrom": _values(ACCOUNT_MODERATABLE),
        }
    return capabilities


def can_moderate_account(user, role, new_status):
    return (
        role == "admin"
        and new_status in ACCOUNT_DECISIONS
        and user.accountStatus in ACCOUNT_MODERATABLE
    )


def can_blacklist(user, role):
    # An admin must never be able to lock out the admin account.
    return role == "admin" and user.role is not Role.ADMIN
