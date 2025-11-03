"""
Task model.
"""
from sqlalchemy import Column, String, Text, DateTime, Enum as SQLEnum, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from ..database import Base


class TaskType(str, enum.Enum):
    """Task type."""
    PROGRAMMING = "programming"
    SETUP = "setup"
    MACHINING = "machining"
    INSPECTION = "inspection"
    OTHER = "other"


class TaskStatus(str, enum.Enum):
    """Task status."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    REVIEW = "review"
    COMPLETED = "completed"


class TaskPriority(str, enum.Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Task(Base):
    """Task model."""

    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    task_type = Column(SQLEnum(TaskType), default=TaskType.OTHER)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, index=True)
    priority = Column(SQLEnum(TaskPriority), default=TaskPriority.MEDIUM)
    assigned_to = Column(String, ForeignKey("users.id"), nullable=True)
    estimated_hours = Column(Float, nullable=True)
    actual_hours = Column(Float, nullable=True)
    dependencies = Column(JSON, default=list)  # Array of task IDs
    blockers = Column(Text, nullable=True)
    files = Column(JSON, default=list)  # Array of file references
    comments = Column(JSON, default=list)  # Array of comment objects
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    job = relationship("Job", back_populates="tasks")
    assignee = relationship("User", back_populates="assigned_tasks")

    def __repr__(self):
        return f"<Task {self.title} - {self.status}>"
