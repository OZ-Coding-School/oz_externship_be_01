import os
from datetime import timedelta

from celery import Celery  # type: ignore

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("oz_externship")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.conf.beat_schedule = {
    "delete-expired-withdrawn-users-every-day-12pm": {
        "task": "apps.users.tasks.delete_expired_withdrawn_users",
        "schedule": timedelta(hours=24),  # 14일이 지난 계정들 매일 정오에 자동으로 삭제
        "options": {"expires": 3600},
    },
}
