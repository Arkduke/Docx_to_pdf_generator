FROM python:3.10-slim

WORKDIR /app

# Install system dependencies, including LibreOffice for conversion
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice \
    && rm -rf /var/lib/apt/lists/*

# Copy shared code
COPY shared/ /app/shared/

# Copy worker service code
COPY worker-service/ /app/worker-service/

# Install Python dependencies
COPY worker-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PYTHONPATH=/app

# Start the worker
CMD ["celery", "-A", "worker-service.tasks.celery_app", "worker", "--loglevel=info", "-c", "1"]
