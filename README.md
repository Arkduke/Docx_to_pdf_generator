# Docx to PDF Generator

This project is a microservices-based application for converting DOCX files to PDF format. It consists of a web API for uploading files and a background worker to handle the conversion process.

## Architecture

The application is composed of two main services:

-   **`api-service`**: A FastAPI application that provides an endpoint for users to upload their `.docx` files. Once a file is received, it is saved, and a task is dispatched to a Celery queue for processing.
-   **`worker-service`**: A Celery worker that listens for tasks from the queue. When a task is received, it uses LibreOffice to convert the specified DOCX file to a PDF.

The two services communicate asynchronously using a Redis message broker for the Celery queue. A PostgreSQL database is used for storing metadata about the files and conversion tasks (though the provided files don't explicitly detail the database models).

## Technology Stack

-   **Backend**: Python
-   **API**: FastAPI
-   **Asynchronous Task Queue**: Celery
-   **Message Broker**: Redis
-   **Database**: PostgreSQL (based on `psycopg2-binary` dependency)
-   **File Conversion**: LibreOffice
-   **Containerization**: Docker

## Services

### API Service (`api-service`)

-   **Framework**: FastAPI
-   **Functionality**: Exposes an HTTP endpoint to accept `.docx` file uploads.
-   **Dependencies**:
    -   `fastapi`
    -   `uvicorn`
    -   `sqlalchemy`
    -   `psycopg2-binary`
    -   `pydantic`
    -   `python-multipart`
    -   `celery`
    -   `redis`

### Worker Service (`worker-service`)

-   **Framework**: Celery
-   **Functionality**: Consumes tasks from the Redis queue and performs the file conversion using a headless instance of LibreOffice.
-   **Dependencies**:
    -   `celery`
    -   `redis`
    -   `sqlalchemy`
    -   `psycopg2-binary`

## Deployment on Railway

This project is configured for deployment on [Railway](https://railway.app/) using a single monorepo.

### Docker Configuration

A single `Dockerfile` is used to build the Docker images for both the `api-service` and the `worker-service`. The `SERVICE_DIR` build argument is used to specify which service the image should be built for. This argument determines:

1.  Which `requirements.txt` file to use for installing Python dependencies.
2.  Which command to run when the container starts, as defined in `entrypoint.sh`.

### Railway Setup

To deploy this project on Railway, you will need to create two separate services from the same repository:

1.  **API Service**:
    -   **Build Path**: `/`
    -   **Dockerfile**: `Dockerfile`
    -   **Build Args**: `SERVICE_DIR=api-service`
    -   **Start Command**: (Handled by `entrypoint.sh`)

2.  **Worker Service**:
    -   **Build Path**: `/`
    -   **Dockerfile**: `Dockerfile`
    -   **Build Args**: `SERVICE_DIR=worker-service`
    -   **Start Command**: (Handled by `entrypoint.sh`)

You will also need to provision a **Redis** database and a **PostgreSQL** database in your Railway project and connect them to your services by setting the appropriate environment variables (e.g., database URLs, Redis URL).

### Entrypoint

The `entrypoint.sh` script is responsible for starting the correct application based on the `SERVICE_DIR` environment variable set during the Docker build.

-   If `SERVICE_DIR` is `api-service`, it starts the FastAPI application using `uvicorn`.
-   If `SERVICE_DIR` is `worker-service`, it starts the Celery worker.

This setup allows for a streamlined build and deployment process from a single codebase.
