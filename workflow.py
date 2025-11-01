#!/usr/bin/env python3
"""
Shop Steward Workflow Management

Manages CNC programming workflow including job assignment, timing, and status tracking.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class Job:
    """Represents a CNC programming job."""
    job_id: str
    customer: str
    part_number: str
    revision: str
    status: str  # INTAKE, QUEUED, IN_PROGRESS, REVIEW, READY, COMPLETED
    programmer: Optional[str] = None
    created_at: float = 0.0
    assigned_at: Optional[float] = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    reviewed_at: Optional[float] = None
    priority: int = 1  # 1=low, 2=normal, 3=high, 4=urgent
    notes: List[str] = None

    def __post_init__(self):
        if self.created_at == 0.0:
            self.created_at = time.time()
        if self.notes is None:
            self.notes = []

    def to_dict(self) -> dict:
        """Convert job to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'Job':
        """Create job from dictionary."""
        return cls(**data)

    def elapsed_time(self, state: str = None) -> Optional[float]:
        """
        Calculate elapsed time for the job or specific state.

        Args:
            state: If specified, calculate time in that state
                   (IN_PROGRESS, REVIEW, etc.)

        Returns:
            Elapsed time in seconds, or None if not applicable
        """
        if state == 'IN_PROGRESS' and self.started_at:
            end_time = self.completed_at or time.time()
            return end_time - self.started_at
        elif state == 'REVIEW' and self.completed_at:
            end_time = self.reviewed_at or time.time()
            return end_time - self.completed_at
        else:
            # Total time from creation
            return time.time() - self.created_at

    def programming_time(self) -> Optional[float]:
        """Get actual programming time (started to completed)."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None


class WorkflowManager:
    """Manages CNC programming workflow and job tracking."""

    def __init__(self, workflow_dir: str):
        """
        Initialize the workflow manager.

        Args:
            workflow_dir: Directory to store workflow data
        """
        self.workflow_dir = Path(workflow_dir)
        self.workflow_dir.mkdir(parents=True, exist_ok=True)

        self.jobs_file = self.workflow_dir / 'jobs.json'
        self.programmers_file = self.workflow_dir / 'programmers.json'

        self.jobs: Dict[str, Job] = {}
        self.programmers: Dict[str, dict] = {}

        self.load_data()

    def load_data(self):
        """Load jobs and programmer data from disk."""
        # Load jobs
        if self.jobs_file.exists():
            with open(self.jobs_file, 'r') as f:
                jobs_data = json.load(f)
                self.jobs = {jid: Job.from_dict(jdata) for jid, jdata in jobs_data.items()}

        # Load programmers
        if self.programmers_file.exists():
            with open(self.programmers_file, 'r') as f:
                self.programmers = json.load(f)

    def save_data(self):
        """Save jobs and programmer data to disk."""
        # Save jobs
        jobs_data = {jid: job.to_dict() for jid, job in self.jobs.items()}
        with open(self.jobs_file, 'w') as f:
            json.dump(jobs_data, f, indent=2)

        # Save programmers
        with open(self.programmers_file, 'w') as f:
            json.dump(self.programmers, f, indent=2)

    def create_job(self, customer: str, part_number: str, revision: str,
                   priority: int = 2, notes: str = None) -> Job:
        """
        Create a new programming job.

        Args:
            customer: Customer name
            part_number: Part number
            revision: Revision level
            priority: Job priority (1-4)
            notes: Optional notes about the job

        Returns:
            Created Job object
        """
        job_id = f"{customer}_{part_number}_{revision}_{int(time.time())}"

        job = Job(
            job_id=job_id,
            customer=customer,
            part_number=part_number,
            revision=revision,
            status='INTAKE',
            priority=priority
        )

        if notes:
            job.notes.append(f"{datetime.now().isoformat()}: {notes}")

        self.jobs[job_id] = job
        self.save_data()

        return job

    def assign_job(self, job_id: str, programmer: str) -> bool:
        """
        Assign a job to a programmer.

        Args:
            job_id: Job ID to assign
            programmer: Programmer name

        Returns:
            True if successful
        """
        if job_id not in self.jobs:
            return False

        job = self.jobs[job_id]
        job.programmer = programmer
        job.status = 'QUEUED'
        job.assigned_at = time.time()

        # Update programmer workload
        if programmer not in self.programmers:
            self.programmers[programmer] = {'active_jobs': 0, 'completed_jobs': 0}

        self.programmers[programmer]['active_jobs'] = self.programmers[programmer].get('active_jobs', 0) + 1

        self.save_data()
        return True

    def start_job(self, job_id: str) -> bool:
        """
        Mark a job as started (programmer begins work).

        Args:
            job_id: Job ID to start

        Returns:
            True if successful
        """
        if job_id not in self.jobs:
            return False

        job = self.jobs[job_id]
        job.status = 'IN_PROGRESS'
        job.started_at = time.time()

        self.save_data()
        return True

    def complete_job(self, job_id: str, notes: str = None) -> bool:
        """
        Mark a job as completed (programming done, awaiting review).

        Args:
            job_id: Job ID to complete
            notes: Optional completion notes

        Returns:
            True if successful
        """
        if job_id not in self.jobs:
            return False

        job = self.jobs[job_id]
        job.status = 'REVIEW'
        job.completed_at = time.time()

        if notes:
            job.notes.append(f"{datetime.now().isoformat()}: {notes}")

        self.save_data()
        return True

    def approve_job(self, job_id: str, notes: str = None) -> bool:
        """
        Approve a job (reviewed and ready for production).

        Args:
            job_id: Job ID to approve
            notes: Optional approval notes

        Returns:
            True if successful
        """
        if job_id not in self.jobs:
            return False

        job = self.jobs[job_id]
        job.status = 'READY'
        job.reviewed_at = time.time()

        if notes:
            job.notes.append(f"{datetime.now().isoformat()}: {notes}")

        # Update programmer stats
        if job.programmer and job.programmer in self.programmers:
            self.programmers[job.programmer]['active_jobs'] -= 1
            self.programmers[job.programmer]['completed_jobs'] = \
                self.programmers[job.programmer].get('completed_jobs', 0) + 1

        self.save_data()
        return True

    def get_jobs_by_status(self, status: str) -> List[Job]:
        """Get all jobs with a specific status."""
        return [job for job in self.jobs.values() if job.status == status]

    def get_jobs_by_programmer(self, programmer: str) -> List[Job]:
        """Get all jobs assigned to a programmer."""
        return [job for job in self.jobs.values() if job.programmer == programmer]

    def get_programmer_workload(self, programmer: str) -> dict:
        """
        Get workload metrics for a programmer.

        Returns:
            Dictionary with active_jobs, completed_jobs, avg_time, etc.
        """
        if programmer not in self.programmers:
            return {'active_jobs': 0, 'completed_jobs': 0, 'capacity': 0}

        active_jobs = len([j for j in self.jobs.values()
                          if j.programmer == programmer and j.status in ['QUEUED', 'IN_PROGRESS']])

        completed_jobs = len([j for j in self.jobs.values()
                             if j.programmer == programmer and j.status in ['READY', 'COMPLETED']])

        # Calculate average programming time
        completed_with_time = [j for j in self.jobs.values()
                              if j.programmer == programmer and j.programming_time() is not None]

        avg_time = None
        if completed_with_time:
            avg_time = sum(j.programming_time() for j in completed_with_time) / len(completed_with_time)

        # Estimate capacity (0-100%)
        # Assume max capacity is 10 active jobs
        capacity = min(100, (active_jobs / 10.0) * 100)

        return {
            'programmer': programmer,
            'active_jobs': active_jobs,
            'completed_jobs': completed_jobs,
            'avg_programming_time_hours': avg_time / 3600 if avg_time else None,
            'capacity_percent': capacity
        }

    def get_available_programmers(self, max_capacity: float = 80.0) -> List[dict]:
        """
        Get programmers with available capacity.

        Args:
            max_capacity: Maximum capacity threshold (%)

        Returns:
            List of programmer workload dicts sorted by capacity
        """
        all_programmers = list(self.programmers.keys())
        workloads = [self.get_programmer_workload(p) for p in all_programmers]

        available = [w for w in workloads if w['capacity_percent'] < max_capacity]
        return sorted(available, key=lambda x: x['capacity_percent'])

    def suggest_programmer(self, priority: int = 2) -> Optional[str]:
        """
        Suggest best programmer for a new job based on workload.

        Args:
            priority: Job priority (higher priority jobs go to less loaded programmers)

        Returns:
            Programmer name or None
        """
        available = self.get_available_programmers()

        if not available:
            return None

        # For high priority, assign to least loaded programmer
        if priority >= 3:
            return available[0]['programmer']
        else:
            # For normal priority, assign to any available programmer
            # Could add more sophisticated logic here
            return available[0]['programmer']

    def generate_report(self, status: str = None) -> str:
        """
        Generate a status report.

        Args:
            status: If specified, only include jobs with this status

        Returns:
            Formatted report string
        """
        jobs_to_report = self.jobs.values()
        if status:
            jobs_to_report = [j for j in jobs_to_report if j.status == status]

        report = ["\n" + "="*80]
        report.append(f"WORKFLOW STATUS REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("="*80 + "\n")

        # Group by status
        status_groups = {}
        for job in jobs_to_report:
            if job.status not in status_groups:
                status_groups[job.status] = []
            status_groups[job.status].append(job)

        for status_name, jobs in status_groups.items():
            report.append(f"\n{status_name} ({len(jobs)} jobs)")
            report.append("-" * 40)

            for job in sorted(jobs, key=lambda x: x.priority, reverse=True):
                priority_str = ['', 'LOW', 'NORMAL', 'HIGH', 'URGENT'][job.priority]
                report.append(f"  {job.part_number}-{job.revision} ({job.customer})")
                report.append(f"    Priority: {priority_str}")
                if job.programmer:
                    report.append(f"    Programmer: {job.programmer}")
                if job.started_at:
                    elapsed = job.elapsed_time('IN_PROGRESS')
                    report.append(f"    Programming time: {elapsed/3600:.1f} hours")
                report.append("")

        # Programmer summary
        report.append("\n" + "="*80)
        report.append("PROGRAMMER WORKLOAD")
        report.append("="*80)

        for programmer in sorted(self.programmers.keys()):
            workload = self.get_programmer_workload(programmer)
            report.append(f"\n{programmer}:")
            report.append(f"  Active jobs: {workload['active_jobs']}")
            report.append(f"  Completed jobs: {workload['completed_jobs']}")
            report.append(f"  Capacity: {workload['capacity_percent']:.0f}%")
            if workload['avg_programming_time_hours']:
                report.append(f"  Avg programming time: {workload['avg_programming_time_hours']:.1f} hours")

        report.append("\n" + "="*80 + "\n")

        return "\n".join(report)
