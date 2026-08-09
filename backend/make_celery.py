# 8 aug 26
# Christiano Fernandes
# make_celery.py
# worker / beat entry point
#
#   celery -A make_celery worker --loglevel INFO
#   celery -A make_celery beat   --loglevel INFO
#
# Worker and beat are separate processes. Beat only schedules; it never executes.


from app import create_app

flask_app = create_app()
celery_app = flask_app.extensions["celery"]
