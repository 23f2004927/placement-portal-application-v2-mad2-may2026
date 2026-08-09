# 4 aug 26 updated
# Christiano Fernandes
# __init__.py
# application factory


from flask import Flask

from app.celery_app import celery_init_app
from app.config import Config
from app.extensions import cache, cors, db, jwt
from app.routes import (
    applications_bp,
    auth_bp,
    companies_bp,
    drives_bp,
    exports_bp,
    notifications_bp,
    profile_bp,
    stats_bp,
    students_bp,
)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.register_blueprint(auth_bp)
    app.register_blueprint(applications_bp)
    app.register_blueprint(drives_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(companies_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(exports_bp)
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, origins=["http://localhost:5173"])
    cache.init_app(app)
    celery_init_app(app)

    from app import models
    from app import tasks  # registers the task decorators

    return app
