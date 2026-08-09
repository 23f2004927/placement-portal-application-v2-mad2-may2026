# 9 aug 26
# Christiano Fernandes
# tasks package
#
# Imported by create_app() purely so the decorators run and the tasks register
# themselves with Celery. Nothing here is called at import time.
#
# Every name below must match a "task" string in beat_schedule (config.py) or a
# .delay() call site — the name string is the only link between the two processes.


from app.tasks.exports import student_applications_csv  # noqa: F401
from app.tasks.health import boom, ping  # noqa: F401
from app.tasks.reminders import daily_student_reminders  # noqa: F401
from app.tasks.reports import monthly_placement_report  # noqa: F401
