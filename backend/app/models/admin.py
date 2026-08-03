# 4 aug 26 updated
# Christiano Fernandes
# admin.py
# admin model


from app.extensions import db


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

    userId = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True)
    user = db.relationship("User", backref=db.backref("admin", uselist=False))
