from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.delivery"]
)

celery_app.conf.beat_schedule = {
    "calculate-delivery-every-5-minutes": {
        "task": "app.tasks.delivery.рассчитать_стоимость_доставки",
        "schedule": 300,  # 5 минут
    },
} 