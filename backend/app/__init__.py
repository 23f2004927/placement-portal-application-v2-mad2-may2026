# 4 aug 26 updated
# Christiano Fernandes
# __init__.py
# application factory


from flask import Flask, jsonify

from app.celery_app import celery_init_app
from app.config import Config
from app.extensions import cache, cors, db, jwt
from app.routes import (
    analytics_bp,
    applications_bp,
    ats_bp,
    auth_bp,
    companies_bp,
    drives_bp,
    exports_bp,
    notifications_bp,
    profile_bp,
    resumes_bp,
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
    app.register_blueprint(analytics_bp)
    app.register_blueprint(ats_bp)
    app.register_blueprint(resumes_bp)

    # MAX_CONTENT_LENGTH aborts before the view runs and Flask's default 413 is
    # HTML, which the frontend reads as an empty message. This makes it JSON so
    # the student sees why the upload failed.
    @app.errorhandler(413)
    def too_large(error):
        return jsonify(message="That file is too large. Maximum 2 MB."), 413

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, origins=["http://localhost:5173"])
    cache.init_app(app)
    celery_init_app(app)

    from app import models
    from app import tasks  # registers the task decorators

    return app
