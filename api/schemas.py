from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from uuid import UUID
import datetime

class FileStatus(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    filename: str = Field(..., alias='original_filename')
    status: str
    error_message: Optional[str] = None

class JobStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    job_id: UUID = Field(..., alias='id')
    status: str
    created_at: datetime.datetime
    files: List[FileStatus]
    download_url: Optional[str] = None

class JobCreatedResponse(BaseModel):
    job_id: UUID
    file_count: int