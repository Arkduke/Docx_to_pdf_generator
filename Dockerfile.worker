FROM python:3.10-slim

WORKDIR /app

# Install system dependencies, including LibreOffice for conversion
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice \
    && rm -rf /var/lib/apt/lists/*

# Install Python libraries
COPY worker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy both worker and api code into the container
COPY ./worker /app/worker
COPY ./api /app/api