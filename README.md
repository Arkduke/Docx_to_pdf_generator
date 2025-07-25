# DocX to PDF Converter - Railway Compatible

A microservices-based document conversion service that converts DOCX files to PDF format, designed for deployment on Railway.

## 🏗️ Architecture

This application consists of two independent microservices:

### API Service (`api-service/`)
- **Technology**: FastAPI
- **Purpose**: Handles HTTP requests, file uploads, and job management
- **Storage**: Files stored in PostgreSQL database as BLOBs
- **Communication**: Sends tasks to worker via Celery/Redis

### Worker Service (`worker-service/`)
- **Technology**: Celery + LibreOffice
- **Purpose**: Performs DOCX to PDF conversion
- **Processing**: Uses LibreOffice headless mode for conversion
- **Storage**: Stores converted files back to PostgreSQL

### Shared Components (`shared/`)
- Database models and utilities
- Celery configuration
- CRUD operations

## 🚀 Deployment Options

### Railway (Recommended)
See [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md) for detailed instructions.

### Local Testing
```bash
# Test the new structure locally
docker-compose -f docker-compose.test.yml up
```

### Traditional Docker
```bash
# Build API service
docker build -f api-service/Dockerfile -t docx-api .

# Build Worker service  
docker build -f worker-service/Dockerfile -t docx-worker .
```

## 📋 Prerequisites

- PostgreSQL database
- Redis instance
- Docker (for containerized deployment)

## 🔧 Environment Variables

### API Service
```bash
DATABASE_URL=postgresql://user:password@host:port/dbname
CELERY_BROKER_URL=redis://host:port/0
CELERY_RESULT_BACKEND=redis://host:port/0
BASE_URL=https://your-domain.com
```

### Worker Service
```bash
DATABASE_URL=postgresql://user:password@host:port/dbname
CELERY_BROKER_URL=redis://host:port/0
CELERY_RESULT_BACKEND=redis://host:port/0
```

## 📡 API Endpoints

### Submit Conversion Job
```http
POST /api/v1/jobs
Content-Type: multipart/form-data

files: [DOCX files]
```

### Check Job Status
```http
GET /api/v1/jobs/{job_id}
```

### Download Results
```http
GET /api/v1/jobs/{job_id}/download
```

## 🔄 Migration from Docker Compose

If you're migrating from the original docker-compose setup:

1. The new structure eliminates shared volumes
2. Files are now stored in the database
3. Services are completely independent
4. Follow the Railway deployment guide

## 🧪 Testing

```bash
# Submit a test job
curl -X POST "http://localhost:8000/api/v1/jobs" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@test.docx"

# Check job status (replace JOB_ID)
curl "http://localhost:8000/api/v1/jobs/JOB_ID"

# Download results
curl "http://localhost:8000/api/v1/jobs/JOB_ID/download" -o results.zip
```

## 📊 Key Benefits

- ✅ **Railway Compatible**: No docker-compose dependencies
- ✅ **Independent Scaling**: Scale API and worker separately  
- ✅ **No Shared Volumes**: Database-based file storage
- ✅ **Cloud Native**: Uses external PostgreSQL and Redis
- ✅ **Fault Tolerant**: Services can restart independently

## 🛠️ Development

### Local Development Setup
1. Clone the repository
2. Copy environment files: `cp api-service/.env.example api-service/.env`
3. Update environment variables
4. Run: `docker-compose -f docker-compose.test.yml up`

### Project Structure
```
├── api-service/           # FastAPI service
│   ├── main.py           # API endpoints
│   ├── schemas.py        # Pydantic models
│   ├── Dockerfile        # API container
│   └── requirements.txt  # Python dependencies
├── worker-service/        # Celery worker
│   ├── tasks.py          # Conversion tasks
│   ├── Dockerfile        # Worker container
│   └── requirements.txt  # Python dependencies
├── shared/               # Shared components
│   ├── models.py         # Database models
│   ├── database.py       # DB configuration
│   └── crud.py           # Database operations
└── RAILWAY_DEPLOYMENT.md # Deployment guide
```

## 🐛 Troubleshooting

- **Database Connection**: Verify `DATABASE_URL` format
- **Celery Issues**: Check Redis connection and worker logs
- **LibreOffice**: Ensure worker container has LibreOffice installed
- **File Size Limits**: PostgreSQL BLOB limits may affect large files

## 📄 License

[Add your license here]
