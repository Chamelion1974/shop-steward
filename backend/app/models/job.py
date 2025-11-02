"""
Job model.
"""
from sqlalchemy import Column, String, Text, DateTime, Enum as SQLEnum, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from ..database import Base


class JobPriority(str, enum.Enum):
    """Job priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class JobStatus(str, enum.Enum):
    """Job status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Job(Base):
    """Job model."""

    __tablename__ = "jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_number = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    customer = Column(String)
    priority = Column(SQLEnum(JobPriority), default=JobPriority.MEDIUM)
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING, index=True)
    deadline = Column(DateTime, nullable=True)
    files = Column(JSON, default=list)  # Array of file references
    metadata = Column(JSON, default=dict)  # Additional job-specific data
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    assigned_to = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    creator = relationship("User", back_populates="created_jobs", foreign_keys=[created_by])
    assignee = relationship("User", back_populates="assigned_jobs", foreign_keys=[assigned_to])
    tasks = relationship("Task", back_populates="job", cascade="all, delete-orphan")
    activity_logs = relationship("ActivityLog", back_populates="job")

    def __repr__(self):
        return f"<Job {self.job_number} - {self.title}>"
