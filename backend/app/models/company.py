# 4 aug 26 updated
# Christiano Fernandes
# company.py
# company  model


from app.extensions import db


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), nullable=False)
    industry = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    hrContactName = db.Column(db.String(80), nullable=True)
    hrContactEmail = db.Column(db.String(100), nullable=True)
    website = db.Column(db.String(255), nullable=True)

    userId = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True)
    user = db.relationship("User", backref=db.backref("company", uselist=False))
