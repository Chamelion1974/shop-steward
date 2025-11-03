"""
Job schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from ..models.job import JobPriority, JobStatus


class JobBase(BaseModel):
    """Base job schema."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    customer: Optional[str] = None
    priority: JobPriority = JobPriority.MEDIUM
    deadline: Optional[datetime] = None


class JobCreate(JobBase):
    """Job creation schema."""
    job_number: Optional[str] = None  # Auto-generated if not provided
    assigned_to: Optional[str] = None
    job_metadata: Dict[str, Any] = {}


class JobUpdate(BaseModel):
    """Job update schema."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    customer: Optional[str] = None
    priority: Optional[JobPriority] = None
    status: Optional[JobStatus] = None
    deadline: Optional[datetime] = None
    assigned_to: Optional[str] = None
    job_metadata: Optional[Dict[str, Any]] = None


class JobResponse(JobBase):
    """Job response schema."""
    id: str
    job_number: str
    status: JobStatus
    files: List[Dict[str, Any]]
    job_metadata: Dict[str, Any]
    created_by: str
    assigned_to: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    """Job list response schema."""
    total: int
    jobs: List[JobResponse]
