import os
import subprocess
import zipfile
import uuid
import logging
import tempfile
import io
from celery import Celery
import sys
sys.path.append('/app')

from shared.database import get_session_local
from shared import models, crud

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Celery
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

celery_app = Celery("worker.tasks", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND, include=['worker-service.tasks'])

# Initialize database session
SessionLocal = get_session_local()

@celery_app.task(name="convert_doc_to_pdf")
def convert_doc_to_pdf(job_id: str, filename: str):
    """
    Converts a docx file to PDF.
    Returns the original filename on success, None on failure.
    """
    db = SessionLocal()
    job_id_uuid = uuid.UUID(job_id)
    try:
        logger.info(f"Starting conversion for {filename} in job {job_id}")
        
        # Get file from database
        file_record = crud.get_file_by_job_and_filename(db, job_id_uuid, filename)
        if not file_record or not file_record.original_file_data:
            raise FileNotFoundError(f"File data not found: {filename}")

        # Create temporary files for processing
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as input_temp:
            input_temp.write(file_record.original_file_data)
            input_temp_path = input_temp.name

        with tempfile.TemporaryDirectory() as temp_dir:
            # Convert using LibreOffice
            result = subprocess.run(
                ["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", temp_dir, input_temp_path],
                check=True, 
                timeout=120,
                capture_output=True,
                text=True
            )
            
            # Find the generated PDF
            pdf_filename = os.path.splitext(os.path.basename(input_temp_path))[0] + '.pdf'
            pdf_path = os.path.join(temp_dir, pdf_filename)
            
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF was not generated: {pdf_path}")
            
            # Read PDF data
            with open(pdf_path, 'rb') as pdf_file:
                pdf_data = pdf_file.read()
            
            # Store PDF in database
            crud.update_file_converted_data(db, job_id_uuid, filename, pdf_data)
            crud.update_file_status(db, job_id_uuid, filename, models.JobStatus.COMPLETED)
            
            logger.info(f"Successfully converted {filename} for job {job_id}")
            return filename # Return filename on success
            
    except Exception as e:
        logger.error(f"Failed to convert {filename} for job {job_id}: {e}")
        crud.update_file_status(db, job_id_uuid, filename, models.JobStatus.FAILED, error=str(e))
        return None # Return None on failure
    finally:
        # Clean up temporary file
        try:
            os.unlink(input_temp_path)
        except:
            pass
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

        # Create zip in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for original_filename in successful_filenames:
                # Get file record from database
                file_record = crud.get_file_by_job_and_filename(db, job_id_uuid, original_filename)
                
                if file_record and file_record.converted_file_data:
                    # Construct the expected PDF filename
                    pdf_filename = os.path.splitext(original_filename)[0] + '.pdf'
                    
                    # Add PDF data to zip
                    zipf.writestr(pdf_filename, file_record.converted_file_data)
                    logger.info(f"Added to zip: {pdf_filename}")
                else:
                    logger.warning(f"Task for '{original_filename}' succeeded, but PDF data not found in database")

        # Store zip data in database
        zip_data = zip_buffer.getvalue()
        crud.update_job_zip_data(db, job_id_uuid, zip_data)
        crud.update_job_status(db, job_id_uuid, models.JobStatus.COMPLETED)
        
        logger.info(f"Successfully created zip archive for job {job_id_uuid}")

    except Exception as e:
        logger.error(f"Fatal error creating zip for job {job_id_uuid}: {e}", exc_info=True)
        crud.update_job_status(db, job_id_uuid, models.JobStatus.FAILED)
    finally:
        db.close()
