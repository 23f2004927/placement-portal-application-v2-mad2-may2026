# 4 aug 26 updated
# Christiano Fernandes
# __init__.py
# application factory


from flask import Flask

from app.config import Config
from app.extensions import cors, db, jwt
from app.routes import auth_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(auth_bp)
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, origins=["http://localhost:5173"])

    from app import models
    return app
