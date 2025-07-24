import os
import subprocess
import zipfile
import uuid
import logging
from celery import Celery
from api.database import SessionLocal
from api import models, crud

# Setup logging
logger = logging.getLogger(__name__)

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

celery_app = Celery("worker.tasks", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND, include=['worker.tasks'])

UPLOADS_DIR = "/app/uploads"
RESULTS_DIR = "/app/results"

@celery_app.task(name="convert_doc_to_pdf")
def convert_doc_to_pdf(job_id: str, filename: str):
    """
    Converts a docx file to PDF.
    Returns the original filename on success, None on failure.
    """
    db = SessionLocal()
    job_id_uuid = uuid.UUID(job_id)
    try:
        job_upload_dir = os.path.join(UPLOADS_DIR, job_id)
        job_result_dir = os.path.join(RESULTS_DIR, job_id)
        os.makedirs(job_result_dir, exist_ok=True)

        input_path = os.path.join(job_upload_dir, filename)
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        subprocess.run(
            ["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", job_result_dir, input_path],
            check=True, timeout=120
        )
        
        crud.update_file_status(db, job_id_uuid, filename, models.JobStatus.COMPLETED)
        return filename # Return filename on success
    except Exception as e:
        logger.error(f"Failed to convert {filename} for job {job_id}: {e}")
        crud.update_file_status(db, job_id_uuid, filename, models.JobStatus.FAILED, error=str(e))
        return None # Return None on failure
    finally:
        db.close()

@celery_app.task(name="create_zip_archive")
def create_zip_archive(conversion_results: list, job_id: str):
    """
    Creates a zip archive from a list of successfully converted filenames.
    This list is passed directly from the chord, making it the source of truth.
    """
    db = SessionLocal()
    job_id_uuid = uuid.UUID(job_id)
    try:
        logger.info(f"Starting zip process for job {job_id_uuid}")
        
        # Filter out `None` results from failed conversions
        successful_filenames = [filename for filename in conversion_results if filename is not None]
        
        if not successful_filenames:
            logger.warning(f"No files were successfully converted for job {job_id_uuid}. Marking job as FAILED.")
            crud.update_job_status(db, job_id_uuid, models.JobStatus.FAILED)
            return

        logger.info(f"Received {len(successful_filenames)} successful filenames from chord for job {job_id_uuid}.")

        job_result_dir = os.path.join(RESULTS_DIR, job_id)
        zip_path = os.path.join(RESULTS_DIR, f"{job_id}.zip")

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for original_filename in successful_filenames:
                # Construct the expected PDF filename
                pdf_filename = os.path.splitext(original_filename)[0] + '.pdf'
                pdf_path = os.path.join(job_result_dir, pdf_filename)
                
                if os.path.exists(pdf_path):
                    logger.info(f"Adding to zip: {pdf_path}")
                    zipf.write(pdf_path, arcname=pdf_filename)
                else:
                    logger.warning(f"Task for '{original_filename}' succeeded, but PDF not found at {pdf_path}")

        crud.update_job_status(db, job_id_uuid, models.JobStatus.COMPLETED)
        logger.info(f"Successfully created zip archive for job {job_id_uuid}")

    except Exception as e:
        logger.error(f"Fatal error creating zip for job {job_id_uuid}: {e}", exc_info=True)
        crud.update_job_status(db, job_id_uuid, models.JobStatus.FAILED)
    finally:
        db.close()