import os
import shutil
import uuid
from typing import List
from celery import chord, signature
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import engine, get_db
from .celery_client import celery_app

app = FastAPI(title="DocX to PDF Conversion Service", description="A robust service to convert DOCX files to PDF asynchronously.")

UPLOADS_DIR = "/app/uploads"
RESULTS_DIR = "/app/results"
BASE_URL = os.getenv("BASE_URL")

@app.on_event("startup")
def startup_event():
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)
    models.Base.metadata.create_all(bind=engine)

@app.post("/api/v1/jobs", response_model=schemas.JobCreatedResponse, status_code=202)
def submit_job(files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    if not files:
        raise HTTPException(status_code=400, detail="No files were provided.")

    job = crud.create_job(db)
    job_id_str = str(job.id)
    job_upload_dir = os.path.join(UPLOADS_DIR, job_id_str)
    os.makedirs(job_upload_dir, exist_ok=True)

    conversion_tasks = []
    file_count = 0
    for upload_file in files:
        if not upload_file.filename.lower().endswith(".docx"):
            continue
        
        file_path = os.path.join(job_upload_dir, upload_file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        
        crud.create_file_record(db, filename=upload_file.filename, job_id=job.id)
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

@app.get("/api/v1/jobs/{job_id}", response_model=schemas.JobStatusResponse)
def get_job_status(job_id: uuid.UUID, db: Session = Depends(get_db)):
    job = crud.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    response = schemas.JobStatusResponse.model_validate(job)
    if response.status == "COMPLETED":
        response.download_url = f"{BASE_URL}/api/v1/jobs/{job_id}/download"
    
    return response

@app.get("/api/v1/jobs/{job_id}/download", response_class=FileResponse)
def download_results(job_id: uuid.UUID, db: Session = Depends(get_db)):
    job = crud.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    if job.status != models.JobStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Job is not yet complete. Current status: " + job.status)

    zip_path = os.path.join(RESULTS_DIR, f"{job_id}.zip")
    if not os.path.exists(zip_path):
        raise HTTPException(status_code=404, detail="Archive file not found. It may have been deleted or failed to create.")

    return FileResponse(
        path=zip_path,
        media_type="application/zip",
        filename=f"conversion_{job_id}.zip"
    )