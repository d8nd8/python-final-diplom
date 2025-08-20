import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "orders.settings")

app = Celery("netology_shop")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")


# Импортируем задачи после инициализации Django
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Настройка периодических задач после инициализации Django"""
    try:
        from backend.tasks import avatar_tasks
        print("✅ Задачи аватарок загружены в Celery")
    except ImportError as e:
        print(f"⚠️  Не удалось загрузить задачи аватарок: {e}")
