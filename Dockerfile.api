FROM python:3.10-slim

WORKDIR /app

# Install Python libraries
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./api /app/api