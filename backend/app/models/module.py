"""
Module model.
"""
from sqlalchemy import Column, String, Text, DateTime, Enum as SQLEnum, JSON
from datetime import datetime
import uuid
import enum

from ..database import Base


class ModuleStatus(str, enum.Enum):
    """Module status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


class Module(Base):
    """Module model for plugin system."""

    __tablename__ = "modules"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False, index=True)
    display_name = Column(String, nullable=False)
    description = Column(Text)
    version = Column(String, nullable=False)
    status = Column(SQLEnum(ModuleStatus), default=ModuleStatus.INACTIVE)
    config = Column(JSON, default=dict)  # Module-specific configuration
    metrics = Column(JSON, default=dict)  # Performance and usage metrics
    last_run = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Module {self.name} - {self.status}>"
