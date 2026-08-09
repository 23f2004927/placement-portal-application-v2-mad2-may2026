# 8 aug 26
# Christiano Fernandes
# celery_app.py
# binds Celery to the Flask application factory
#
# A task runs in a worker process, outside the request cycle, so there is no
# application context and db.session is unusable. The FlaskTask subclass pushes
# one around every call, which is why tasks can query normally.


from celery import Celery, Task


def celery_init_app(app):
    class FlaskTask(Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery = Celery(app.name, task_cls=FlaskTask)
    celery.config_from_object(app.config["CELERY"])

    # set_default() lets @shared_task in app/tasks/ find this instance without
    # importing it, which would be a cycle.
    celery.set_default()
    app.extensions["celery"] = celery
    return celery
