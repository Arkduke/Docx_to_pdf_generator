from sqlalchemy.orm import Session
from . import models
import uuid

def create_job(db: Session) -> models.Job:
    new_job = models.Job(id=uuid.uuid4(), status=models.JobStatus.PENDING)
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job

def create_file_record(db: Session, filename: str, job_id: uuid.UUID) -> models.File:
    new_file = models.File(
        original_filename=filename,
        job_id=job_id,
        status=models.JobStatus.PENDING
    )
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    return new_file

def get_job(db: Session, job_id: uuid.UUID) -> models.Job:
    return db.query(models.Job).filter(models.Job.id == job_id).first()

def update_job_status(db: Session, job_id: uuid.UUID, status: models.JobStatus):
    job = get_job(db, job_id)
    if job:
        job.status = status
        db.commit()

def update_file_status(db: Session, job_id: uuid.UUID, filename: str, status: models.JobStatus, error: str = None):
    file_record = db.query(models.File).filter_by(job_id=job_id, original_filename=filename).first()
    if file_record:
        file_record.status = status
        file_record.error_message = error
        db.commit()