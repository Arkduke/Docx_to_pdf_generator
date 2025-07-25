FROM python:3.10-slim

WORKDIR /app

ENV PYTHONPATH=/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice \
    && rm -rf /var/lib/apt/lists/*

COPY worker-service/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ /app/shared/
COPY worker-service/ /app/worker-service/

WORKDIR /app/worker-service

CMD ["celery", "-A", "tasks.celery_app", "worker", "--loglevel=info", "-c", "1"]
