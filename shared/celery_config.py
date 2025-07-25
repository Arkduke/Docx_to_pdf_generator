import os
from celery import Celery

def get_celery_app(service_name: str) -> Celery:
    """Create and configure Celery app"""
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")
    
    return Celery(
        service_name,
        broker=CELERY_BROKER_URL,
        backend=CELERY_RESULT_BACKEND
    )
