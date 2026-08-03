# 4 aug 26 updated
# Christiano Fernandes
# __init__.py
# application factory


from flask import Flask

from app.config import Config
from app.extensions import db, jwt


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)

    from app import models

    return app
