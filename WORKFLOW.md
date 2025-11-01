# Shop Steward - Workflow Management

Workflow management system for tracking CNC programming jobs from intake through production.

## Overview

The workflow system tracks jobs through these states:

1. **INTAKE** - Files staged by NPI coordinator
2. **QUEUED** - Assigned to programmer, waiting to start
3. **IN_PROGRESS** - Programmer actively working
4. **REVIEW** - Programming complete, awaiting verification
5. **READY** - Approved and ready for production
6. **COMPLETED** - Job finished and archived

## Quick Start

### 1. Add Programmers

```bash
python workflow_cli.py add-programmer "John Smith"
python workflow_cli.py add-programmer "Jane Doe"
```

### 2. Create a Job

```bash
python workflow_cli.py create "AcmeCorp" "ABC-123" "A" --priority 3
# Creates job: AcmeCorp_ABC-123_A_1234567890
```

### 3. Assign to Programmer

```bash
# Manual assignment
python workflow_cli.py assign AcmeCorp_ABC-123_A_1234567890 --programmer "John Smith"

# Auto-assign based on workload
python workflow_cli.py assign AcmeCorp_ABC-123_A_1234567890 --auto
```

### 4. Start Programming

```bash
python workflow_cli.py start AcmeCorp_ABC-123_A_1234567890
```

### 5. Complete Programming

```bash
python workflow_cli.py complete AcmeCorp_ABC-123_A_1234567890 --notes "All toolpaths verified"
```

### 6. Approve for Production

```bash
python workflow_cli.py approve AcmeCorp_ABC-123_A_1234567890 --notes "Machine assignment: Mill-3"
```

## Commands Reference

### Job Management

```bash
# Create a new job
python workflow_cli.py create <customer> <part> <revision> [options]
  --priority <1-4>    Priority level (1=low, 2=normal, 3=high, 4=urgent)
  --notes "text"      Notes about the job

# Assign job to programmer
python workflow_cli.py assign <job_id> [options]
  --programmer "name" Specific programmer name
  --auto              Auto-assign based on workload
  --priority <1-4>    Priority for auto-assignment

# Start a job
python workflow_cli.py start <job_id>

# Complete a job (moves to REVIEW status)
python workflow_cli.py complete <job_id> [--notes "text"]

# Approve a job (moves to READY status)
python workflow_cli.py approve <job_id> [--notes "text"]
```

### Reporting & Monitoring

```bash
# List all jobs
python workflow_cli.py list

# List jobs by status
python workflow_cli.py list --status IN_PROGRESS

# List jobs by programmer
python workflow_cli.py list --programmer "John Smith"

# Show programmer workload
python workflow_cli.py workload

# Show specific programmer workload
python workflow_cli.py workload --programmer "John Smith"

# Generate status report
python workflow_cli.py report

# Generate status report for specific state
python workflow_cli.py report --status REVIEW
```

### Programmer Management

```bash
# Add a new programmer
python workflow_cli.py add-programmer "Name"
```

## Workflow States Explained

### INTAKE
- Initial state when job is created
- NPI coordinator has staged files
- Awaiting programmer assignment

### QUEUED
- Job assigned to programmer
- In programmer's queue
- Not yet started

### IN_PROGRESS
- Programmer actively working on job
- Timer running to track programming time
- Files being created/modified

### REVIEW
- Programming completed
- Awaiting review/verification
- In "purgatory" state as described in requirements
- Ready for machine assignment

### READY
- Reviewed and approved
- Final form achieved
- Ready for production
- Programs proven

### COMPLETED
- Job finished
- Archived for historical tracking

## Metrics & Analytics

The system automatically tracks:

- **Programming Time**: Actual time from start to completion
- **Queue Time**: Time waiting in queue before starting
- **Review Time**: Time in review/purgatory
- **Total Cycle Time**: End-to-end time from intake to ready

### Programmer Metrics

For each programmer:
- Active jobs count
- Completed jobs count
- Average programming time
- Capacity utilization (0-100%)

### Workload Management

The system estimates capacity based on:
- Active job count (max 10 = 100% capacity)
- Job priorities
- Historical completion times

Auto-assignment considers:
- Current workload
- Job priority
- Historical performance

## Integration with File Organization

The workflow system works alongside the file organization system:

1. **NPI Intake**: Files dropped into monitored directory
2. **Auto-Organization**: Shop Steward organizes files into structure
3. **Job Creation**: Workflow job created automatically or manually
4. **Programmer Assignment**: Job assigned based on workload
5. **Programming**: Programmer works in organized folder structure
6. **Completion**: Files moved to final state, job marked complete
7. **Review**: Quality check in organized structure
8. **Production**: Proven programs ready, job marked READY

## Example Workflow

```bash
# 1. Add programmers (one-time setup)
python workflow_cli.py add-programmer "Alice"
python workflow_cli.py add-programmer "Bob"

# 2. NPI coordinator creates job
python workflow_cli.py create "TechCorp" "TC-9000" "B" \
  --priority 3 \
  --notes "Rush order - due Friday"

# Output: Created job: TechCorp_TC-9000_B_1699123456

# 3. Auto-assign to available programmer
python workflow_cli.py assign TechCorp_TC-9000_B_1699123456 --auto
# Output: Auto-assigning to: Alice

# 4. Alice starts work
python workflow_cli.py start TechCorp_TC-9000_B_1699123456

# 5. Alice completes programming
python workflow_cli.py complete TechCorp_TC-9000_B_1699123456 \
  --notes "All 5 ops programmed and simulated"

# 6. Check review queue
python workflow_cli.py list --status REVIEW

# 7. Supervisor approves
python workflow_cli.py approve TechCorp_TC-9000_B_1699123456 \
  --notes "Assigned to Mill-2, prove-out Tuesday"

# 8. Check overall status
python workflow_cli.py report
```

## Workload Report Example

```
Programmer Workload:
================================================================================

Alice:
  Active jobs: 3
  Completed jobs: 15
  Capacity: 30%
  Avg programming time: 4.2 hours

  Active jobs:
    - TC-9000-B (IN_PROGRESS)
    - ABC-123-A (QUEUED)
    - XYZ-456-C (QUEUED)

Bob:
  Active jobs: 7
  Completed jobs: 12
  Capacity: 70%
  Avg programming time: 5.1 hours

  Active jobs:
    - PART-111-A (IN_PROGRESS)
    - PART-222-B (IN_PROGRESS)
    - PART-333-A (QUEUED)
    ...
```

## Data Storage

Workflow data is stored in JSON files:

```
.workflow/
├── jobs.json          # All job data
└── programmers.json   # Programmer statistics
```

These files are human-readable and can be backed up, version-controlled, or integrated with other systems.

## Best Practices

1. **Create jobs immediately** when files arrive from customers
2. **Use auto-assignment** to balance workload fairly
3. **Set priorities accurately** to ensure urgent jobs get attention
4. **Add completion notes** for knowledge retention
5. **Check workload regularly** to identify bottlenecks
6. **Generate reports daily** to track progress
7. **Archive completed jobs** but never delete (knowledge preservation)

## Future Enhancements

Planned features:
- Dashboard web interface
- Email notifications for status changes
- Integration with ERP systems
- Advanced scheduling algorithms
- Historical analytics and trends
- Customer delivery estimates
- Resource planning and forecasting

## Troubleshooting

### Job not found
- Verify job_id is correct
- Check `list` command to see all jobs

### Cannot assign job
- Ensure programmer has been added with `add-programmer`
- Check job is in INTAKE status

### Workload shows 0 jobs
- Ensure jobs are assigned to that programmer
- Check if programmer name is spelled correctly

## Support

For issues or questions, refer to main README.md or open an issue on GitHub.
