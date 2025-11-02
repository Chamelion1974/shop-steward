"""
User model.
"""
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from ..database import Base


class UserRole(str, enum.Enum):
    """User role enum."""
    HUB_MASTER = "hub_master"
    HUB_CAP = "hub_cap"


class User(Base):
    """User model."""

    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.HUB_CAP)
    skills = Column(JSON, default=list)  # Array of skills for Hub Caps
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    created_jobs = relationship("Job", back_populates="creator", foreign_keys="Job.created_by")
    assigned_jobs = relationship("Job", back_populates="assignee", foreign_keys="Job.assigned_to")
    assigned_tasks = relationship("Task", back_populates="assignee")
    activity_logs = relationship("ActivityLog", back_populates="user")

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
