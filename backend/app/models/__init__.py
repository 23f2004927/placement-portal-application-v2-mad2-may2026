# 4 aug 26 updated
# Christiano Fernandes
# __init__.py
# aggregates model imports so `from app import models` registers all tables


from app.models.admin import Admin
from app.models.application import Application, ApplicationStatus
from app.models.company import Company
from app.models.drive import Drive, DriveStatus, JobType
from app.models.notification import Notification
from app.models.offer_letter import OfferLetter
from app.models.placement import Placement
from app.models.student import Branch, Student
from app.models.user import AccountStatus, Role, User
