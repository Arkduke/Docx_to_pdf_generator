FROM python:3.10-slim

WORKDIR /app

ENV PYTHONPATH=/app

COPY api-service/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


COPY shared/ /app/shared/
COPY api-service/ /app/api-service/

WORKDIR /app/api-service

EXPOSE 8000


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
