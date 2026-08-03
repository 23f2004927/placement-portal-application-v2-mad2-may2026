# 3 aug 26 updated
# Christiano Fernandes
# user.py
# user model



from werkzeug.security import check_password_hash, generate_password_hash
from app.extensions import db
import enum

class Role(enum.Enum):
    ADMIN = "admin"
    COMPANY = "company"
    STUDENT = "student"

class AccountStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(80), unique=True, nullable=False)
    passwordHash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(Role),nullable=False)
    accountStatus = db.Column(db.Enum(AccountStatus),nullable=False)
    blackListed = db.Column(db.Boolean, nullable=False)


    def setPassword(self, passwordIn):
        self.passwordHash = generate_password_hash(passwordIn)

    def checkPassword(self, passwordIn):
        return check_password_hash(self.passwordHash, passwordIn)
