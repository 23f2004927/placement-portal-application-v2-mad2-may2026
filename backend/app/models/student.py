# 3 aug 26 updated
# Christiano Fernandes
# student.py
# student model


from app.extensions import db
import enum

class Branch(enum.Enum):
    COMPUTER = "computer"
    ELECTRONICS = "electronics"
    ELECTRICAL = "electrical"
    MECHANICAL = "mechanical"
    CIVIL = "civil"
    CHEMICAL = "chemical"
    INFORMATION_TECHNOLOGY = "information_technology"
    ELECTRONICS_AND_TELECOMMUNICATION = "electronics_and_telecommunication"
    AI_ML = "ai_ml"
    DATA_SCIENCE = "data_science"
    ROBOTICS = "robotics"
    BIOMEDICAL = "biomedical"
    AEROSPACE = "aerospace"
    AUTOMOBILE = "automobile"
    INDUSTRIAL = "industrial"
    MINING = "mining"
    METALLURGY = "metallurgy"
    ENVIRONMENTAL = "environmental"


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email =  db.Column(db.String(100), unique=True, nullable=False)
    phoneNumber = db.Column(db.String(10), nullable=False)
    rollNumber = db.Column(db.String(20),nullable=False)
    branch = db.Column(db.Enum(Branch),nullable=False)
    yearStudy = db.Column(db.String(3), nullable=False)
    gradeYear = db.Column(db.Integer, nullable=False)
    cgpa = db.Column(db.Float(10), nullable=False)
    links = db.Column(db.JSON, nullable=True)
    resume = db.Column(db.String(255), nullable=True)
    userId = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True)
    user = db.relationship("User", backref=db.backref("student", uselist=False))
