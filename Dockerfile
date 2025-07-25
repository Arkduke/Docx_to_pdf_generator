FROM python:3.10-slim

WORKDIR /app

ENV PYTHONPATH=/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice \
    && rm -rf /var/lib/apt/lists/*

COPY . .

ARG SERVICE_DIR

# Promote the build-time ARG to a runtime ENV variable
ENV SERVICE_DIR=${SERVICE_DIR}

RUN if [ -z "$SERVICE_DIR" ]; then echo "Error: SERVICE_DIR build-arg is not set." && exit 1; fi

RUN pip install --no-cache-dir -r ${SERVICE_DIR}/requirements.txt

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set the entrypoint. It will now read the SERVICE_DIR environment
# variable directly, so no CMD is needed to pass arguments.
ENTRYPOINT ["/entrypoint.sh"]
