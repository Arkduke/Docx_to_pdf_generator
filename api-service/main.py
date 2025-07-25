import os
import uuid
import io
import zipfile
from typing import List
from celery import chord
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import sys
sys.path.append('/app')

from shared import crud, models
from shared.database import get_session_local, create_tables
from shared.celery_config import get_celery_app

# Import schemas from current package
try:
    from .schemas import JobCreatedResponse, JobStatusResponse
except ImportError:
    from schemas import JobCreatedResponse, JobStatusResponse

app = FastAPI(title="DocX to PDF Conversion Service", description="A robust service to convert DOCX files to PDF asynchronously.")

# Initialize database session
SessionLocal = get_session_local()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize Celery
celery_app = get_celery_app("api_service")

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

@app.on_event("startup")
def startup_event():
    create_tables()

@app.post("/api/v1/jobs", response_model=JobCreatedResponse, status_code=202)
def submit_job(files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    if not files:
        raise HTTPException(status_code=400, detail="No files were provided.")

    job = crud.create_job(db)
    job_id_str = str(job.id)

    conversion_tasks = []
    file_count = 0
    for upload_file in files:
        if not upload_file.filename.lower().endswith(".docx"):
            continue
        
        # Read file data
        file_data = upload_file.file.read()
        
        # Store file in database
        crud.create_file_record(db, filename=upload_file.filename, job_id=job.id, file_data=file_data)
        
        # Create a signature for each conversion task
        task_sig = celery_app.signature("convert_doc_to_pdf", args=[job_id_str, upload_file.filename])
        conversion_tasks.append(task_sig)
        file_count += 1
    
    if file_count == 0:
        crud.update_job_status(db, job.id, models.JobStatus.FAILED)
        raise HTTPException(status_code=400, detail="No valid .docx files were uploaded.")

    # Define the callback task that will run after all conversions are done
    zip_callback = celery_app.signature("create_zip_archive", args=[job_id_str])

    # Create and apply the chord
    chord(conversion_tasks)(zip_callback)

    crud.update_job_status(db, job.id, models.JobStatus.IN_PROGRESS)
    return {"job_id": job.id, "file_count": file_count}

@app.get("/api/v1/jobs/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: uuid.UUID, db: Session = Depends(get_db)):
    job = crud.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    response = JobStatusResponse.model_validate(job)
    if response.status == "COMPLETED":
        response.download_url = f"{BASE_URL}/api/v1/jobs/{job_id}/download"
    
    return response

@app.get("/api/v1/jobs/{job_id}/download")
def download_results(job_id: uuid.UUID, db: Session = Depends(get_db)):
    job = crud.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    if job.status != models.JobStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Job is not yet complete. Current status: " + job.status)

    if not job.zip_data:
        raise HTTPException(status_code=404, detail="Archive file not found. It may have been deleted or failed to create.")

    # Create a BytesIO object from the zip data
    zip_buffer = io.BytesIO(job.zip_data)
    
    return StreamingResponse(
        io.BytesIO(job.zip_data),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=conversion_{job_id}.zip"}
    )
