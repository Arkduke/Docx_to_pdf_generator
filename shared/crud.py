from sqlalchemy.orm import Session
from typing import Optional
import uuid
from .models import Job, File, JobStatus

def create_job(db: Session) -> Job:
    """Create a new job"""
    job = Job()
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def get_job(db: Session, job_id: uuid.UUID) -> Optional[Job]:
    """Get a job by ID"""
    return db.query(Job).filter(Job.id == job_id).first()

def update_job_status(db: Session, job_id: uuid.UUID, status: JobStatus):
    """Update job status"""
    db.query(Job).filter(Job.id == job_id).update({"status": status})
    db.commit()

def update_job_zip_data(db: Session, job_id: uuid.UUID, zip_data: bytes):
    """Update job with zip data"""
    db.query(Job).filter(Job.id == job_id).update({"zip_data": zip_data})
    db.commit()

def create_file_record(db: Session, filename: str, job_id: uuid.UUID, file_data: bytes) -> File:
    """Create a file record with data"""
    file_record = File(
        original_filename=filename,
        job_id=job_id,
        original_file_data=file_data
    )
    db.add(file_record)
    db.commit()
    db.refresh(file_record)
    return file_record

def get_file_by_job_and_filename(db: Session, job_id: uuid.UUID, filename: str) -> Optional[File]:
    """Get a file by job ID and filename"""
    return db.query(File).filter(File.job_id == job_id, File.original_filename == filename).first()

def update_file_status(db: Session, job_id: uuid.UUID, filename: str, status: JobStatus, error: str = None):
    """Update file status"""
    query = db.query(File).filter(File.job_id == job_id, File.original_filename == filename)
    update_data = {"status": status}
    if error:
        update_data["error_message"] = error
    query.update(update_data)
    db.commit()

def update_file_converted_data(db: Session, job_id: uuid.UUID, filename: str, converted_data: bytes):
    """Update file with converted PDF data"""
    db.query(File).filter(
        File.job_id == job_id, 
        File.original_filename == filename
    ).update({"converted_file_data": converted_data})
    db.commit()

def get_files_by_job(db: Session, job_id: uuid.UUID):
    """Get all files for a job"""
    return db.query(File).filter(File.job_id == job_id).all()
