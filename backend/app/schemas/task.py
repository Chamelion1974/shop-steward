"""
Task schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from ..models.task import TaskType, TaskStatus, TaskPriority


class TaskComment(BaseModel):
    """Task comment schema."""
    id: str
    user_id: str
    username: str
    text: str
    created_at: datetime


class TaskCommentCreate(BaseModel):
    """Task comment creation schema."""
    text: str = Field(..., min_length=1)


class TaskBase(BaseModel):
    """Base task schema."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    task_type: TaskType = TaskType.OTHER
    priority: TaskPriority = TaskPriority.MEDIUM
    estimated_hours: Optional[float] = Field(None, ge=0)


class TaskCreate(TaskBase):
    """Task creation schema."""
    job_id: str
    assigned_to: Optional[str] = None
    dependencies: List[str] = []


class TaskUpdate(BaseModel):
    """Task update schema."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    task_type: Optional[TaskType] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assigned_to: Optional[str] = None
    estimated_hours: Optional[float] = Field(None, ge=0)
    actual_hours: Optional[float] = Field(None, ge=0)
    dependencies: Optional[List[str]] = None
    blockers: Optional[str] = None


class TaskResponse(TaskBase):
    """Task response schema."""
    id: str
    job_id: str
    status: TaskStatus
    assigned_to: Optional[str]
    actual_hours: Optional[float]
    dependencies: List[str]
    blockers: Optional[str]
    files: List[Dict[str, Any]]
    comments: List[TaskComment]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Task list response schema."""
    total: int
    tasks: List[TaskResponse]
