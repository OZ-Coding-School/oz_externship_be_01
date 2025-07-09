import os

from celery import Celery  # type: ignore
from celery.schedules import crontab  # type: ignore

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("oz_externsblahip")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.conf.beat_schedule = {
    "delete-expired-withdrawn-users-every-day-12pm": {
        "task": "apps.users.tasks.delete_expired_withdrawn_users",
        "schedule": crontab(hour=0),  # 매일 12시 정각에 실행
        "options": {"expires": 3600},
    },
}
