"""
Tasks API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import uuid

from ..database import get_db
from ..models.user import User, UserRole
from ..models.task import Task, TaskStatus
from ..models.job import Job
from ..schemas.task import (
    TaskCreate, TaskUpdate, TaskResponse, TaskListResponse,
    TaskCommentCreate, TaskComment
)
from ..core.auth import get_current_active_user, require_hub_master


router = APIRouter()


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    job_id: Optional[str] = None,
    status: Optional[TaskStatus] = None,
    assigned_to: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List tasks with optional filters.
    Hub Caps can only see tasks assigned to them or unassigned tasks.
    Hub Masters can see all tasks.
    """
    query = db.query(Task)

    # Apply role-based filtering
    if current_user.role == UserRole.HUB_CAP:
        query = query.filter(
            (Task.assigned_to == current_user.id) | (Task.assigned_to == None)
        )

    # Apply filters
    if job_id:
        query = query.filter(Task.job_id == job_id)
    if status:
        query = query.filter(Task.status == status)
    if assigned_to:
        query = query.filter(Task.assigned_to == assigned_to)

    # Get total count
    total = query.count()

    # Get paginated results
    tasks = query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()

    return TaskListResponse(total=total, tasks=tasks)


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new task.
    """
    # Verify job exists
    job = db.query(Job).filter(Job.id == task_data.job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # Create task
    task = Task(
        id=str(uuid.uuid4()),
        job_id=task_data.job_id,
        title=task_data.title,
        description=task_data.description,
        task_type=task_data.task_type,
        priority=task_data.priority,
        estimated_hours=task_data.estimated_hours,
        assigned_to=task_data.assigned_to,
        dependencies=task_data.dependencies
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific task by ID.
    """
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Check permissions
    if current_user.role == UserRole.HUB_CAP:
        if task.assigned_to and task.assigned_to != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view this task"
            )

    return task


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a task.
    """
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Check permissions
    if current_user.role == UserRole.HUB_CAP:
        if task.assigned_to != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this task"
            )

    # Update fields
    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    # Update completion timestamp if status changed to completed
    if task_data.status == TaskStatus.COMPLETED and not task.completed_at:
        task.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(task)

    return task


@router.post("/{task_id}/comments", response_model=TaskResponse)
async def add_task_comment(
    task_id: str,
    comment_data: TaskCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Add a comment to a task.
    """
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Create comment object
    comment = {
        "id": str(uuid.uuid4()),
        "user_id": current_user.id,
        "username": current_user.username,
        "text": comment_data.text,
        "created_at": datetime.utcnow().isoformat()
    }

    # Add comment to task
    if not task.comments:
        task.comments = []
    task.comments.append(comment)

    db.commit()
    db.refresh(task)

    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hub_master)
):
    """
    Delete a task (Hub Master only).
    """
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    db.delete(task)
    db.commit()

    return None
