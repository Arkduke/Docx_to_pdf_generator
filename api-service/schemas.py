
import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional

class FileStatus(BaseModel):
    original_filename: str
    status: str
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

class JobStatusResponse(BaseModel):
    id: uuid.UUID
    status: str
    created_at: datetime
    files: List[FileStatus]
    download_url: Optional[str] = None

    class Config:
        from_attributes = True

class JobCreatedResponse(BaseModel):
    job_id: uuid.UUID
    file_count: int