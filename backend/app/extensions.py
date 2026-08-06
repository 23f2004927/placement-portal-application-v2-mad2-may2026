# 3 aug 26 updated
# Christiano Fernandes
# extension.py
# hosts imports flask extensions to prevnt circular imports


from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

db = SQLAlchemy()
jwt = JWTManager()
cors =CORS()
