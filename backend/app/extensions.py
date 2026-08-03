# 3 aug 26 updated
# Christiano Fernandes
# extension.py
# hosts imports flask extensions to prevnt circular imports


from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
jwt = JWTManager()
