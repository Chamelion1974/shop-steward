"""
Activity log model for audit trail.
"""
from sqlalchemy import Column, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..database import Base


class ActivityLog(Base):
    """Activity log for tracking all system actions."""

    __tablename__ = "activity_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_type = Column(String, nullable=False, index=True)  # job, task, module, user
    entity_id = Column(String, nullable=False, index=True)
    action = Column(String, nullable=False)  # created, updated, deleted, assigned, etc.
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    details = Column(JSON, default=dict)  # Action-specific details
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="activity_logs")
    # Polymorphic relationships for different entity types
    job = relationship("Job", back_populates="activity_logs", foreign_keys="ActivityLog.entity_id",
                      primaryjoin="and_(ActivityLog.entity_id==Job.id, ActivityLog.entity_type=='job')",
                      viewonly=True)
    task = relationship("Task", back_populates="activity_logs", foreign_keys="ActivityLog.entity_id",
                       primaryjoin="and_(ActivityLog.entity_id==Task.id, ActivityLog.entity_type=='task')",
                       viewonly=True)

    def __repr__(self):
        return f"<ActivityLog {self.action} on {self.entity_type}:{self.entity_id}>"
