"""
Module schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from ..models.module import ModuleStatus


class ModuleBase(BaseModel):
    """Base module schema."""
    display_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")


class ModuleCreate(ModuleBase):
    """Module creation schema."""
    name: str = Field(..., min_length=1, max_length=50, pattern=r"^[a-z0-9_]+$")
    config: Dict[str, Any] = {}


class ModuleUpdate(BaseModel):
    """Module update schema."""
    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    version: Optional[str] = Field(None, pattern=r"^\d+\.\d+\.\d+$")
    status: Optional[ModuleStatus] = None


class ModuleConfig(BaseModel):
    """Module configuration schema."""
    config: Dict[str, Any]


class ModuleResponse(ModuleBase):
    """Module response schema."""
    id: str
    name: str
    status: ModuleStatus
    config: Dict[str, Any]
    metrics: Dict[str, Any]
    last_run: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
