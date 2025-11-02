"""
Jobs API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import uuid

from ..database import get_db
from ..models.user import User, UserRole
from ..models.job import Job, JobStatus
from ..schemas.job import JobCreate, JobUpdate, JobResponse, JobListResponse
from ..core.auth import get_current_active_user, require_hub_master


router = APIRouter()


def generate_job_number(db: Session) -> str:
    """Generate a unique job number."""
    # Format: JOB-YYYYMMDD-NNNN
    today = datetime.now().strftime("%Y%m%d")
    prefix = f"JOB-{today}-"

    # Find the highest number for today
    jobs_today = db.query(Job).filter(
        Job.job_number.like(f"{prefix}%")
    ).order_by(Job.job_number.desc()).first()

    if jobs_today:
        last_num = int(jobs_today.job_number.split("-")[-1])
        new_num = last_num + 1
    else:
        new_num = 1

    return f"{prefix}{new_num:04d}"


@router.get("", response_model=JobListResponse)
async def list_jobs(
    status: Optional[JobStatus] = None,
    assigned_to: Optional[str] = None,
    customer: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List jobs with optional filters.
    Hub Caps can only see jobs assigned to them or unassigned jobs.
    Hub Masters can see all jobs.
    """
    query = db.query(Job)

    # Apply role-based filtering
    if current_user.role == UserRole.HUB_CAP:
        # Hub Caps see jobs assigned to them or unassigned
        query = query.filter(
            (Job.assigned_to == current_user.id) | (Job.assigned_to == None)
        )

    # Apply filters
    if status:
        query = query.filter(Job.status == status)
    if assigned_to:
        query = query.filter(Job.assigned_to == assigned_to)
    if customer:
        query = query.filter(Job.customer.ilike(f"%{customer}%"))

    # Get total count
    total = query.count()

    # Get paginated results
    jobs = query.order_by(Job.created_at.desc()).offset(skip).limit(limit).all()

    return JobListResponse(total=total, jobs=jobs)


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new job.
    """
    # Generate job number if not provided
    job_number = job_data.job_number or generate_job_number(db)

    # Check if job number already exists
    existing = db.query(Job).filter(Job.job_number == job_number).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job number {job_number} already exists"
        )

    # Create job
    job = Job(
        id=str(uuid.uuid4()),
        job_number=job_number,
        title=job_data.title,
        description=job_data.description,
        customer=job_data.customer,
        priority=job_data.priority,
        deadline=job_data.deadline,
        assigned_to=job_data.assigned_to,
        metadata=job_data.metadata,
        created_by=current_user.id
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific job by ID.
    """
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # Check permissions
    if current_user.role == UserRole.HUB_CAP:
        if job.assigned_to and job.assigned_to != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view this job"
            )

    return job


@router.patch("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: str,
    job_data: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a job.
    Hub Masters can update any job.
    Hub Caps can only update status of jobs assigned to them.
    """
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # Check permissions
    if current_user.role == UserRole.HUB_CAP:
        if job.assigned_to != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this job"
            )
        # Hub Caps can only update status
        if any([
            job_data.title, job_data.description, job_data.customer,
            job_data.priority, job_data.deadline, job_data.assigned_to
        ]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Hub Caps can only update job status"
            )

    # Update fields
    update_data = job_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)

    # Update completion timestamp if status changed to completed
    if job_data.status == JobStatus.COMPLETED and not job.completed_at:
        job.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(job)

    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hub_master)
):
    """
    Delete a job (Hub Master only).
    """
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    db.delete(job)
    db.commit()

    return None
