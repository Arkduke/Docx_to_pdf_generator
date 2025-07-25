import uuid
import enum
from sqlalchemy import Column, String, DateTime, Enum as SQLAlchemyEnum, ForeignKey, Text, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Job(Base):
    __tablename__ = "jobs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status = Column(SQLAlchemyEnum(JobStatus), default=JobStatus.PENDING)
    created_at = Column(DateTime, server_default=func.now())
    zip_data = Column(LargeBinary, nullable=True)  # Store the zip file in database
    files = relationship("File", back_populates="job", cascade="all, delete-orphan")

class File(Base):
    __tablename__ = "files"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"))
    original_filename = Column(String, index=True)
    status = Column(SQLAlchemyEnum(JobStatus), default=JobStatus.PENDING)
    error_message = Column(String, nullable=True)
    original_file_data = Column(LargeBinary, nullable=True)  # Store original file in database
    converted_file_data = Column(LargeBinary, nullable=True)  # Store converted PDF in database
    job = relationship("Job", back_populates="files")
