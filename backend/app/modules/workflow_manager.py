"""
Workflow Manager Module - Job Tracking and Assignment

Integrates the workflow.py functionality into The Hub as a module.
"""
from typing import Dict, Any, List, Optional
from pathlib import Path
import sys
from datetime import datetime

# Add root directory to path to import workflow
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from .base import BaseModule

# Import the WorkflowManager class from the CLI tool
try:
    from workflow import WorkflowManager, Job
    WORKFLOW_AVAILABLE = True
except ImportError:
    WORKFLOW_AVAILABLE = False
    WorkflowManager = None
    Job = None


class WorkflowModule(BaseModule):
    """
    Workflow Manager module for job tracking and assignment.

    This module integrates the workflow management system into The Hub,
    providing:
    - Job creation and tracking
    - Programmer assignment with load balancing
    - Time tracking (programming time, review time)
    - Status workflow management
    - Workload metrics and reporting
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="workflow_manager",
            display_name="Workflow Manager",
            version="1.0.0",
            config=config or {}
        )
        self.workflow_manager: Optional[WorkflowManager] = None

    def activate(self) -> bool:
        """Activate the Workflow Manager module."""
        if not WORKFLOW_AVAILABLE:
            self.log_activity("WorkflowManager not available", "error")
            return False

        try:
            # Get configuration
            workflow_dir = self.get_config("workflow_dir", "/data/workflow")

            # Initialize WorkflowManager
            self.workflow_manager = WorkflowManager(workflow_dir=workflow_dir)

            self.log_activity(f"Workflow Manager activated with dir: {workflow_dir}")
            self.update_metrics("activations", 1)

            # Update metrics from workflow data
            self._update_metrics_from_workflow()

            return True

        except Exception as e:
            self.log_activity(f"Failed to activate: {e}", "error")
            return False

    def deactivate(self) -> bool:
        """Deactivate the Workflow Manager module."""
        try:
            if self.workflow_manager:
                self.workflow_manager.save_data()

            self.workflow_manager = None
            self.log_activity("Workflow Manager deactivated")
            return True

        except Exception as e:
            self.log_activity(f"Failed to deactivate: {e}", "error")
            return False

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process workflow actions.

        Args:
            data: Dictionary with:
                - action: 'create_job', 'assign', 'start', 'complete', 'approve', etc.
                - job_id: Job identifier (for most actions)
                - customer, part_number, revision: For create_job
                - programmer: For manual assignment
                - priority: For create_job
                - notes: For adding notes

        Returns:
            dict: Result with job info or error
        """
        if not self.workflow_manager:
            return {
                "success": False,
                "error": "Workflow Manager not activated"
            }

        action = data.get("action")

        try:
            if action == "create_job":
                customer = data.get("customer")
                part_number = data.get("part_number")
                revision = data.get("revision", "A")
                priority = data.get("priority", 1)

                if not all([customer, part_number]):
                    return {
                        "success": False,
                        "error": "customer and part_number required"
                    }

                job_id = self.workflow_manager.create_job(
                    customer=customer,
                    part_number=part_number,
                    revision=revision,
                    priority=priority
                )

                self.increment_metric("jobs_created")
                self.last_run = datetime.utcnow()

                return {
                    "success": True,
                    "job_id": job_id,
                    "job": self.workflow_manager.get_job(job_id).to_dict()
                }

            elif action == "assign":
                job_id = data.get("job_id")
                programmer = data.get("programmer")
                auto_assign = data.get("auto", False)

                if not job_id:
                    return {"success": False, "error": "job_id required"}

                if auto_assign:
                    success = self.workflow_manager.auto_assign_job(job_id)
                elif programmer:
                    success = self.workflow_manager.assign_job(job_id, programmer)
                else:
                    return {"success": False, "error": "programmer or auto=True required"}

                if success:
                    self.increment_metric("jobs_assigned")
                    return {
                        "success": True,
                        "job": self.workflow_manager.get_job(job_id).to_dict()
                    }
                else:
                    return {"success": False, "error": "Assignment failed"}

            elif action == "start":
                job_id = data.get("job_id")
                if not job_id:
                    return {"success": False, "error": "job_id required"}

                success = self.workflow_manager.start_job(job_id)
                if success:
                    self.increment_metric("jobs_started")
                    return {
                        "success": True,
                        "job": self.workflow_manager.get_job(job_id).to_dict()
                    }
                else:
                    return {"success": False, "error": "Start failed"}

            elif action == "complete":
                job_id = data.get("job_id")
                if not job_id:
                    return {"success": False, "error": "job_id required"}

                success = self.workflow_manager.complete_job(job_id)
                if success:
                    self.increment_metric("jobs_completed")
                    return {
                        "success": True,
                        "job": self.workflow_manager.get_job(job_id).to_dict()
                    }
                else:
                    return {"success": False, "error": "Complete failed"}

            elif action == "approve":
                job_id = data.get("job_id")
                if not job_id:
                    return {"success": False, "error": "job_id required"}

                success = self.workflow_manager.approve_job(job_id)
                if success:
                    self.increment_metric("jobs_approved")
                    return {
                        "success": True,
                        "job": self.workflow_manager.get_job(job_id).to_dict()
                    }
                else:
                    return {"success": False, "error": "Approve failed"}

            elif action == "add_note":
                job_id = data.get("job_id")
                note = data.get("note")
                if not all([job_id, note]):
                    return {"success": False, "error": "job_id and note required"}

                self.workflow_manager.add_job_note(job_id, note)
                return {
                    "success": True,
                    "job": self.workflow_manager.get_job(job_id).to_dict()
                }

            elif action == "add_programmer":
                name = data.get("name")
                skills = data.get("skills", [])
                capacity = data.get("capacity", 5)

                if not name:
                    return {"success": False, "error": "name required"}

                self.workflow_manager.add_programmer(name, skills, capacity)
                self.increment_metric("programmers_added")
                return {
                    "success": True,
                    "programmer": self.workflow_manager.programmers.get(name)
                }

            elif action == "get_workload":
                workload = self.workflow_manager.get_workload_report()
                return {
                    "success": True,
                    "workload": workload
                }

            elif action == "list_jobs":
                status_filter = data.get("status")
                programmer_filter = data.get("programmer")

                jobs = self.workflow_manager.list_jobs(
                    status_filter=status_filter,
                    programmer_filter=programmer_filter
                )

                return {
                    "success": True,
                    "jobs": [job.to_dict() for job in jobs]
                }

            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}"
                }

        except Exception as e:
            self.log_activity(f"Error processing {action}: {e}", "error")
            self.increment_metric("errors")
            return {
                "success": False,
                "error": str(e)
            }

    def get_status(self) -> Dict[str, Any]:
        """Get current Workflow Manager status."""
        if not self.workflow_manager:
            return {
                "healthy": False,
                "active": self.is_active,
                "error": "Not activated"
            }

        # Calculate summary stats
        all_jobs = self.workflow_manager.list_jobs()
        programmers = self.workflow_manager.programmers

        job_stats = {
            "total": len(all_jobs),
            "queued": len([j for j in all_jobs if j.status == "QUEUED"]),
            "in_progress": len([j for j in all_jobs if j.status == "IN_PROGRESS"]),
            "review": len([j for j in all_jobs if j.status == "REVIEW"]),
            "ready": len([j for j in all_jobs if j.status == "READY"]),
            "completed": len([j for j in all_jobs if j.status == "COMPLETED"]),
        }

        return {
            "healthy": True,
            "active": self.is_active,
            "config": {
                "workflow_dir": self.get_config("workflow_dir"),
            },
            "stats": {
                "jobs": job_stats,
                "programmers": len(programmers),
            },
            "metrics": self.get_metrics(),
            "last_run": self.last_run.isoformat() if self.last_run else None
        }

    def _update_metrics_from_workflow(self):
        """Update module metrics from workflow data."""
        if not self.workflow_manager:
            return

        all_jobs = self.workflow_manager.list_jobs()

        self.update_metrics("total_jobs", len(all_jobs))
        self.update_metrics("total_programmers", len(self.workflow_manager.programmers))
        self.update_metrics("jobs_in_progress",
                           len([j for j in all_jobs if j.status == "IN_PROGRESS"]))
        self.update_metrics("jobs_completed",
                           len([j for j in all_jobs if j.status == "COMPLETED"]))

    # Convenience methods
    def create_job(self, customer: str, part_number: str, revision: str = "A",
                   priority: int = 1) -> Dict[str, Any]:
        """Convenience method to create a job."""
        return self.process({
            "action": "create_job",
            "customer": customer,
            "part_number": part_number,
            "revision": revision,
            "priority": priority
        })

    def assign_job(self, job_id: str, programmer: str = None, auto: bool = False) -> Dict[str, Any]:
        """Convenience method to assign a job."""
        return self.process({
            "action": "assign",
            "job_id": job_id,
            "programmer": programmer,
            "auto": auto
        })

    def start_job(self, job_id: str) -> Dict[str, Any]:
        """Convenience method to start a job."""
        return self.process({
            "action": "start",
            "job_id": job_id
        })

    def complete_job(self, job_id: str) -> Dict[str, Any]:
        """Convenience method to complete a job."""
        return self.process({
            "action": "complete",
            "job_id": job_id
        })

    def get_workload(self) -> Dict[str, Any]:
        """Convenience method to get workload report."""
        return self.process({
            "action": "get_workload"
        })
