#!/usr/bin/env python3
"""
Shop Steward Workflow CLI

Command-line interface for managing CNC programming workflow.
"""

import argparse
import sys
from pathlib import Path
from workflow import WorkflowManager


def cmd_create_job(args, wf: WorkflowManager):
    """Create a new job."""
    job = wf.create_job(
        customer=args.customer,
        part_number=args.part,
        revision=args.revision,
        priority=args.priority,
        notes=args.notes
    )
    print(f"Created job: {job.job_id}")
    print(f"  Customer: {job.customer}")
    print(f"  Part: {job.part_number}-{job.revision}")
    print(f"  Status: {job.status}")


def cmd_assign_job(args, wf: WorkflowManager):
    """Assign a job to a programmer."""
    if args.auto:
        # Auto-assign based on workload
        programmer = wf.suggest_programmer(priority=args.priority)
        if not programmer:
            print("ERROR: No available programmers")
            return False

        print(f"Auto-assigning to: {programmer}")
    else:
        programmer = args.programmer

    if wf.assign_job(args.job_id, programmer):
        print(f"Assigned job {args.job_id} to {programmer}")
        workload = wf.get_programmer_workload(programmer)
        print(f"  Programmer workload: {workload['active_jobs']} active jobs ({workload['capacity_percent']:.0f}% capacity)")
    else:
        print(f"ERROR: Failed to assign job {args.job_id}")
        return False


def cmd_start_job(args, wf: WorkflowManager):
    """Start a job."""
    if wf.start_job(args.job_id):
        job = wf.jobs[args.job_id]
        print(f"Started job: {job.job_id}")
        print(f"  Part: {job.part_number}-{job.revision}")
        print(f"  Programmer: {job.programmer}")
        print(f"  Status: {job.status}")
    else:
        print(f"ERROR: Failed to start job {args.job_id}")
        return False


def cmd_complete_job(args, wf: WorkflowManager):
    """Complete a job."""
    if wf.complete_job(args.job_id, notes=args.notes):
        job = wf.jobs[args.job_id]
        prog_time = job.programming_time()
        print(f"Completed job: {job.job_id}")
        print(f"  Part: {job.part_number}-{job.revision}")
        print(f"  Status: {job.status} (awaiting review)")
        if prog_time:
            print(f"  Programming time: {prog_time/3600:.2f} hours")
    else:
        print(f"ERROR: Failed to complete job {args.job_id}")
        return False


def cmd_approve_job(args, wf: WorkflowManager):
    """Approve a job."""
    if wf.approve_job(args.job_id, notes=args.notes):
        job = wf.jobs[args.job_id]
        print(f"Approved job: {job.job_id}")
        print(f"  Part: {job.part_number}-{job.revision}")
        print(f"  Status: {job.status} (ready for production)")
    else:
        print(f"ERROR: Failed to approve job {args.job_id}")
        return False


def cmd_list_jobs(args, wf: WorkflowManager):
    """List jobs."""
    if args.status:
        jobs = wf.get_jobs_by_status(args.status)
        print(f"\nJobs with status: {args.status}")
    elif args.programmer:
        jobs = wf.get_jobs_by_programmer(args.programmer)
        print(f"\nJobs assigned to: {args.programmer}")
    else:
        jobs = list(wf.jobs.values())
        print("\nAll jobs:")

    if not jobs:
        print("  (none)")
        return

    print("-" * 80)
    for job in sorted(jobs, key=lambda x: (x.status, -x.priority)):
        priority_str = ['', 'LOW', 'NORMAL', 'HIGH', 'URGENT'][job.priority]
        print(f"{job.job_id}")
        print(f"  Part: {job.part_number}-{job.revision} | Customer: {job.customer}")
        print(f"  Status: {job.status} | Priority: {priority_str}")
        if job.programmer:
            print(f"  Programmer: {job.programmer}")
        if job.started_at:
            elapsed = job.elapsed_time('IN_PROGRESS')
            print(f"  Programming time: {elapsed/3600:.1f} hours")
        print()


def cmd_workload(args, wf: WorkflowManager):
    """Show programmer workload."""
    if args.programmer:
        programmers = [args.programmer]
    else:
        programmers = sorted(wf.programmers.keys())

    print("\nProgrammer Workload:")
    print("=" * 80)

    for programmer in programmers:
        workload = wf.get_programmer_workload(programmer)
        print(f"\n{programmer}:")
        print(f"  Active jobs: {workload['active_jobs']}")
        print(f"  Completed jobs: {workload['completed_jobs']}")
        print(f"  Capacity: {workload['capacity_percent']:.0f}%")
        if workload['avg_programming_time_hours']:
            print(f"  Avg programming time: {workload['avg_programming_time_hours']:.1f} hours")

        # Show active jobs
        active = wf.get_jobs_by_programmer(programmer)
        active = [j for j in active if j.status in ['QUEUED', 'IN_PROGRESS']]
        if active:
            print(f"\n  Active jobs:")
            for job in active:
                print(f"    - {job.part_number}-{job.revision} ({job.status})")


def cmd_report(args, wf: WorkflowManager):
    """Generate status report."""
    report = wf.generate_report(status=args.status)
    print(report)


def cmd_add_programmer(args, wf: WorkflowManager):
    """Add a new programmer."""
    if args.name not in wf.programmers:
        wf.programmers[args.name] = {'active_jobs': 0, 'completed_jobs': 0}
        wf.save_data()
        print(f"Added programmer: {args.name}")
    else:
        print(f"Programmer {args.name} already exists")


def main():
    parser = argparse.ArgumentParser(
        description='Shop Steward Workflow Management - CNC Programming Job Tracking',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--workflow-dir',
        type=str,
        default='./.workflow',
        help='Directory to store workflow data (default: ./.workflow)'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Create job
    create_parser = subparsers.add_parser('create', help='Create a new job')
    create_parser.add_argument('customer', help='Customer name')
    create_parser.add_parser('part', help='Part number')
    create_parser.add_argument('revision', help='Revision level')
    create_parser.add_argument('--priority', type=int, default=2, choices=[1,2,3,4],
                              help='Priority (1=low, 2=normal, 3=high, 4=urgent)')
    create_parser.add_argument('--notes', help='Notes about the job')

    # Assign job
    assign_parser = subparsers.add_parser('assign', help='Assign job to programmer')
    assign_parser.add_argument('job_id', help='Job ID to assign')
    assign_parser.add_argument('--programmer', help='Programmer name')
    assign_parser.add_argument('--auto', action='store_true',
                              help='Auto-assign based on workload')
    assign_parser.add_argument('--priority', type=int, default=2,
                              help='Job priority for auto-assignment')

    # Start job
    start_parser = subparsers.add_parser('start', help='Start a job')
    start_parser.add_argument('job_id', help='Job ID to start')

    # Complete job
    complete_parser = subparsers.add_parser('complete', help='Mark job as completed')
    complete_parser.add_argument('job_id', help='Job ID to complete')
    complete_parser.add_argument('--notes', help='Completion notes')

    # Approve job
    approve_parser = subparsers.add_parser('approve', help='Approve job for production')
    approve_parser.add_argument('job_id', help='Job ID to approve')
    approve_parser.add_argument('--notes', help='Approval notes')

    # List jobs
    list_parser = subparsers.add_parser('list', help='List jobs')
    list_parser.add_argument('--status', help='Filter by status')
    list_parser.add_argument('--programmer', help='Filter by programmer')

    # Workload
    workload_parser = subparsers.add_parser('workload', help='Show programmer workload')
    workload_parser.add_argument('--programmer', help='Show specific programmer')

    # Report
    report_parser = subparsers.add_parser('report', help='Generate status report')
    report_parser.add_argument('--status', help='Filter by status')

    # Add programmer
    prog_parser = subparsers.add_parser('add-programmer', help='Add a new programmer')
    prog_parser.add_argument('name', help='Programmer name')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize workflow manager
    wf = WorkflowManager(args.workflow_dir)

    # Execute command
    commands = {
        'create': cmd_create_job,
        'assign': cmd_assign_job,
        'start': cmd_start_job,
        'complete': cmd_complete_job,
        'approve': cmd_approve_job,
        'list': cmd_list_jobs,
        'workload': cmd_workload,
        'report': cmd_report,
        'add-programmer': cmd_add_programmer
    }

    if args.command in commands:
        result = commands[args.command](args, wf)
        if result is False:
            sys.exit(1)
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
