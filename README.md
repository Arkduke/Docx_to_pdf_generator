# DocX to PDF Conversion Service

A robust, scalable, and cloud-ready microservice for converting DOCX files to PDF. Built with FastAPI, Celery, and LibreOffice, and designed for easy deployment on both local Docker environments and cloud platforms like Railway.

## Table of Contents

- [✨ Key Features](#-key-features)
- [🏗️ Architecture](#️-architecture)
- [🚀 Deployment](#-deployment)
- [🔧 Environment Configuration](#-environment-configuration)
- [📡 API Documentation](#-api-documentation)
- [🧪 Testing](#-testing)
- [🛠️ Development & Contribution](#️-development--contribution)
- [📊 Monitoring & Troubleshooting](#-monitoring--troubleshooting)
- [🔒 Advanced Self-Hosting](#-advanced-self-hosting)
- [📄 License](#-license)

---

## ✨ Key Features

-   ✅ **Asynchronous Processing**: Upload multiple DOCX files and get them converted without blocking.
-   ✅ **Independent Scaling**: Scale the API and conversion workers separately to meet demand.
-   ✅ **Cloud Native**: Designed to use external PostgreSQL and Redis, making it perfect for platforms like Railway.
-   ✅ **Database-Driven**: Uses the database for file storage, eliminating the need for shared volumes.
-   ✅ **Job Tracking**: Monitor the status of each conversion job from pending to completion.
-   ✅ **Batch Processing**: Convert multiple files in a single API call, which are then returned as a `.zip` archive.
-   ✅ **Fault Tolerant**: Microservices can restart independently, ensuring high availability.

---

## 🏗️ Architecture

The application uses a microservices-based architecture to separate concerns and enhance scalability.

```
┌───────────┐     ┌──────────────┐      ┌────────────────┐
│  Client   ├────►│ FastAPI API  ├─────►│ Celery Workers │
│ (Uploads) │     │(Job & File Mgmt)│     │ (PDF Conversion) │
└───────────┘     └───────┬──────┘      └────────┬───────┘
                          │                      │
                          │   ┌──────────────┐   │
                          └─► │    Redis     │◄──┘
                              │ (Task Queue) │
                          ┌─► └──────────────┘◄──┐
                          │                      │
                          │   ┌──────────────┐   │
                          └─► │  PostgreSQL  │◄──┘
                              │ (Job & File DB)│
                              └──────────────┘
```

### Components

1.  **API Service (`api-service/`)**: A **FastAPI** application that handles HTTP requests, file uploads, and job management. It sends conversion tasks to the worker via a Redis queue.
2.  **Worker Service (`worker-service/`)**: A **Celery** worker that listens for tasks. It uses **LibreOffice** in headless mode to perform the actual DOCX to PDF conversion.
3.  **Shared Components (`shared/`)**: A common library containing database models (SQLAlchemy), Celery configuration, and CRUD operations used by both the API and the worker.

### Project Structure

```
.
├── api-service/          # FastAPI service
│   ├── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── worker-service/         # Celery worker
│   ├── tasks.py
│   ├── Dockerfile
│   └── requirements.txt
├── shared/                 # Shared components (DB models, etc.)
│   ├── models.py
│   └── database.py
├── docker-compose.yml      # Main compose file for local deployment
├── .env.example            # Environment variable template
└── RAILWAY_DEPLOYMENT.md   # Detailed guide for Railway
```

---

## 🚀 Deployment

This service can be deployed on Railway or run locally using Docker Compose.

### Option 1: Railway (Recommended)

For a seamless cloud deployment with automatic builds, networking, and database provisioning, follow the detailed guide:

➡️ [**RAILWAY_DEPLOYMENT.md**](./RAILWAY_DEPLOYMENT.md)

### Option 2: Local Deployment with Docker Compose

#### Prerequisites

-   **Docker** (version 20.0 or higher)
-   **Docker Compose** (version 2.0 or higher)
-   **Git**

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-folder>
```

#### 2. Configure Environment

Create a `.env` file by copying the example file. This will store your configuration for all services.

```bash
cp .env.example .env
```

Now, open the `.env` file and review the default settings. For local deployment, the defaults are usually sufficient.

#### 3. Launch Services

Build and run the containers in detached mode:

```bash
docker-compose up --build -d
```

#### 4. Verify Deployment

Check that all containers are running correctly:

```bash
docker-compose ps
```

You should see `api`, `worker`, `db`, and `redis` services with a `running` status. The API will be available at `http://localhost:8000`.

---

## 🔧 Environment Configuration

All configuration is managed via environment variables defined in the `.env` file or your cloud platform's secrets management.

| Variable                | Service(s)    | Description                               | Default (for local)                            |
| ----------------------- | ------------- | ----------------------------------------- | ---------------------------------------------- |
| `POSTGRES_USER`         | `db`          | PostgreSQL database username.             | `user`                                         |
| `POSTGRES_PASSWORD`     | `db`          | PostgreSQL database password.             | `your_secure_password`                         |
| `POSTGRES_DB`           | `db`          | The name of the database.                 | `doc_converter_db`                             |
| `DATABASE_URL`          | `api`, `worker` | Full connection string for PostgreSQL.    | `postgresql://user:password@db:5432/dbname`    |
| `CELERY_BROKER_URL`     | `api`, `worker` | Connection URL for the Redis task broker. | `redis://redis:6379/0`                         |
| `CELERY_RESULT_BACKEND` | `api`, `worker` | Connection URL for the Redis result backend. | `redis://redis:6379/0`                         |
| `BASE_URL`              | `api`         | Public base URL for creating download links. | `http://localhost:8000`                        |

---

## 📡 API Documentation

**Base URL (Local):** `http://localhost:8000`

### 1. Submit Conversion Job

Upload one or more DOCX files to start a new conversion job.

-   **Endpoint**: `POST /api/v1/jobs`
-   **Content-Type**: `multipart/form-data`
-   **Parameters**: `files` (one or more DOCX files)

**Example Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/jobs" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@/path/to/document1.docx" \
  -F "files=@/path/to/document2.docx"
```

**Success Response (202 Accepted):**

```json
{
  "job_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "file_count": 2
}
```

### 2. Get Job Status

Check the status of a previously submitted job.

-   **Endpoint**: `GET /api/v1/jobs/{job_id}`

**Example Request:**

```bash
curl "http://localhost:8000/api/v1/jobs/a1b2c3d4-e5f6-7890-1234-567890abcdef"
```

**Success Response (200 OK):**

```json
{
  "job_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "status": "COMPLETED",
  "created_at": "2025-07-25T10:30:00Z",
  "files": [
    {
      "filename": "document1.docx",
      "status": "COMPLETED",
      "error_message": null
    },
    {
      "filename": "document2.docx",
      "status": "COMPLETED",
      "error_message": null
    }
  ],
  "download_url": "http://localhost:8000/api/v1/jobs/a1b2c3d4-e5f6-7890-1234-567890abcdef/download"
}
```

### 3. Download Results

Download a `.zip` archive containing all successfully converted PDF files for a job.

-   **Endpoint**: `GET /api/v1/jobs/{job_id}/download`

**Example Request:**

```bash
curl "http://localhost:8000/api/v1/jobs/a1b2c3d4-e5f6-7890-1234-567890abcdef/download" \
  --output results.zip
```

### Status Values

-   `PENDING`: The job has been accepted and is waiting in the queue.
-   `IN_PROGRESS`: The job is actively being processed by a worker.
-   `COMPLETED`: The job finished, and all files were converted successfully.
-   `PARTIAL_FAILURE`: The job finished, but one or more files failed to convert.
-   `FAILED`: The entire job failed due to a critical error.

---

## 🧪 Testing

To test the service, you can use the `curl` examples above.

1.  **Submit a job** with a test `.docx` file.
2.  **Check the status** using the returned `job_id`.
3.  Once the status is `COMPLETED`, **download the results** zip file.

---

## 🛠️ Development & Contribution

Interested in contributing? Here’s how to set up a local development environment.

1.  **Start Infrastructure**: Run only the database and Redis services with Docker.
    ```bash
    docker-compose up -d db redis
    ```
2.  **Set Environment**: Ensure your `.env` file is configured correctly.
3.  **Run API Service Locally**:
    ```bash
    cd api-service/
    pip install -r requirements.txt
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```
4.  **Run Worker Service Locally**:
    ```bash
    cd worker-service/
    pip install -r requirements.txt
    celery -A tasks.celery_app worker --loglevel=info
    ```

Now you can make changes to the API or worker and they will reload automatically.

---

## 📊 Monitoring & Troubleshooting

### Viewing Logs

You can view real-time logs for any service:

```bash
# View logs for all services
docker-compose logs -f

# View logs for a specific service (e.g., worker)
docker-compose logs -f worker
```

### Common Issues

-   **Database/Redis Connection Errors**: Verify that the `DATABASE_URL` and `CELERY_BROKER_URL` in your `.env` file are correct and that the `db` and `redis` containers are running.
-   **LibreOffice Conversion Fails**: Check the worker logs for errors related to LibreOffice. Ensure it's correctly installed in the `worker-service/Dockerfile`.
-   **File Size Limits**: Be aware of potential file size limitations imposed by your database (e.g., PostgreSQL's `BLOB` type).

---

## 🔒 Advanced Self-Hosting

For production deployments, consider the following:

-   **Security**: Always change default passwords and restrict access to your database and Redis instances. Use a reverse proxy like Nginx or Traefik to handle SSL/TLS termination.
-   **Scaling**: You can easily scale the number of conversion workers to handle higher loads:
    ```bash
    docker-compose up --build -d --scale worker=3
    ```
-   **Data Persistence**: The `docker-compose.yml` is configured to use Docker volumes for PostgreSQL and Redis data, ensuring it persists across container restarts. For production, you may want to use managed database services instead.
-   **Backups**: Regularly back up your PostgreSQL database.
    ```bash
    docker-compose exec -T db pg_dump -U <user> -d <dbname> > backup.sql
    ```

---

## 📄 License

[Add Your License Here (e.g., MIT, Apache 2.0)]
