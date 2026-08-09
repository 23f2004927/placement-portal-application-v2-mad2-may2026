# 8 aug 26
# Christiano Fernandes
# offer_letter.py
# offer letter model
#
# The terms are COPIED here rather than read back through the drive. A drive can
# still be edited after an offer goes out; a letter that silently changed its
# salary afterwards would be worthless as a record.


from app.extensions import db


class OfferLetter(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Unique: one letter per application. Re-issuing is a 409, not a second row.
    applicationId = db.Column(
        db.Integer, db.ForeignKey("application.id"), nullable=False, unique=True
    )

    issuedAt = db.Column(db.DateTime, server_default=db.func.now())

    # Snapshot of the offer at the moment it was issued.
    roleTitle = db.Column(db.String(150), nullable=False)
    companyName = db.Column(db.String(120), nullable=False)
    jobType = db.Column(db.String(30), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    salary = db.Column(db.Float, nullable=True)
    joiningDate = db.Column(db.Date, nullable=True)

    application = db.relationship(
        "Application", backref=db.backref("offerLetter", uselist=False)
    )
