import os
from celery import Celery, signature

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

celery_app = Celery(
    "api_client",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)