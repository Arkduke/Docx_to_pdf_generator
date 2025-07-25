#!/bin/sh

# This script determines which service to start based on the
# SERVICE_DIR environment variable passed during the build.

# The last command in the Dockerfile (`CMD`) sets "$1" to be the service directory name.
SERVICE_NAME="$1"

# Change to the directory of the service we want to run
cd /app/${SERVICE_NAME}

# Execute the command for the specific service
if [ "$SERVICE_NAME" = "api-service" ]; then
  echo "Starting api-service..."
  exec uvicorn main:app --host 0.0.0.0 --port 8000

elif [ "$SERVICE_NAME" = "worker-service" ]; then
  echo "Starting worker-service..."
  exec celery -A tasks.celery_app worker --loglevel=info -c 1

else
  echo "Error: Unknown service name '$SERVICE_NAME'"
  exit 1
fi
