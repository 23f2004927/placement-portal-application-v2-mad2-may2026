# 10 aug 26
# Christiano Fernandes
# placement.py
# placement model — the institute's register of who ended up where
#
# Written when a student ACCEPTS an offer, never before. A placement is the
# outcome of an application, so it carries applicationId and cannot exist
# without one: a student cannot be placed with no application on record.
#
# The terms are copied rather than joined through, for the same reason the
# offer letter copies them — a drive stays editable after the fact, and last
# year's placement register must not change when someone edits a posting.


from app.extensions import db


class Placement(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    studentId = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    companyId = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)

    # Unique: accepting twice is already blocked by the status check, and this
    # makes a duplicate row impossible even if that check were ever bypassed.
    applicationId = db.Column(
        db.Integer, db.ForeignKey("application.id"), nullable=False, unique=True
    )

    position = db.Column(db.String(150), nullable=False)
    salary = db.Column(db.Float, nullable=True)
    joiningDate = db.Column(db.Date, nullable=True)
    placedAt = db.Column(db.DateTime, server_default=db.func.now())

    student = db.relationship("Student", backref="placements")
    company = db.relationship("Company", backref="placements")
    application = db.relationship(
        "Application", backref=db.backref("placement", uselist=False)
    )
