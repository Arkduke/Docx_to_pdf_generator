#!/bin/sh

# This script determines which service to start based on the
# SERVICE_DIR environment variable, which is baked into the image.

# Check if the environment variable is set
if [ -z "$SERVICE_DIR" ]; then
  echo "Error: SERVICE_DIR environment variable is not set."
  exit 1
fi

# Change to the directory of the service we want to run
cd /app/${SERVICE_DIR}

# Execute the command for the specific service
if [ "$SERVICE_DIR" = "api-service" ]; then
  echo "Starting api-service..."
  exec uvicorn main:app --host 0.0.0.0 --port 8000

elif [ "$SERVICE_DIR" = "worker-service" ]; then
  echo "Starting worker-service..."
  exec celery -A tasks.celery_app worker --loglevel=info -c 1

else
  echo "Error: Unknown service name '$SERVICE_DIR'"
  exit 1
fi
