# Shop Steward - The Hub Architecture

## Overview

**The Hub** is the central command center and dashboard for the Shop Steward production management ecosystem. It serves as the portal where jobs enter the system, are monitored, assigned, and tracked through completion.

## System Philosophy

The Hub is the **Shop Steward at the system level** - a comprehensive solution for production floor management that coordinates multiple specialized modules and serves different user roles with tailored interfaces.

## User Roles

### Hub Master (Administrator)
The production manager who oversees the entire system:
- Deploy and configure modules (Housekeeper, Manufacturing Intelligence, etc.)
- Monitor system health and module effectiveness
- Manage user accounts and permissions
- View high-level analytics and reports
- Configure job workflows and routing rules

### Hub Caps (CNC Programmers)
The production team members who execute work:
- Receive task assignments
- Provide task status updates
- Collaborate with team members
- Upload completed work files
- Push jobs through the completion portal

## Architecture Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
  - High-performance async API
  - Automatic OpenAPI documentation
  - WebSocket support for real-time updates

- **Database**: PostgreSQL
  - SQLAlchemy ORM for data models
  - Alembic for migrations
  - Support for complex queries and analytics

- **Authentication**: JWT-based auth
  - Role-based access control (RBAC)
  - Secure password hashing (bcrypt)
  - Token refresh mechanism

- **Real-time Communication**: WebSockets
  - Live job status updates
  - Team collaboration features
  - System notifications

### Frontend
- **Framework**: React 18 with TypeScript
  - Type-safe component development
  - Modern hooks-based architecture
  - Efficient re-rendering

- **Styling**: Tailwind CSS
  - Utility-first styling
  - Responsive design
  - Custom theme for immersive UI

- **State Management**: React Context + React Query
  - Server state management
  - Optimistic updates
  - Automatic cache invalidation

- **UI Components**:
  - shadcn/ui (headless components)
  - Recharts for data visualization
  - Framer Motion for animations

- **Real-time**: WebSocket client
  - Auto-reconnection
  - Message queuing
  - Event-based updates

## Core System Components

### 1. Job Portal
The entry point for all production work:
- Job creation and specification
- File upload (CAD files, specs, etc.)
- Priority and deadline management
- Customer/project association

### 2. Shop Task Manager
The intelligent task orchestration system:
- Automatic task breakdown from jobs
- Smart task assignment (skill-based, load-balanced)
- Dependency tracking
- Progress monitoring
- Bottleneck detection

### 3. Module System
Plugin architecture for specialized capabilities:
- **Manufacturing Intelligence**: CNC program analysis and optimization
- **Housekeeper**: Automated file organization and cleanup
- **Hall Monitor**: Resource monitoring and alerting
- Extensible for future modules

### 4. Collaboration Hub
Team communication and coordination:
- Task-specific chat/comments
- @mentions and notifications
- File sharing
- Status updates and handoffs

### 5. Analytics Engine
Data-driven insights:
- Production metrics
- Team performance
- Module effectiveness
- Bottleneck analysis
- Time tracking

## Database Schema

### Core Entities

#### Users
```sql
- id (UUID)
- username (unique)
- email (unique)
- hashed_password
- role (hub_master | hub_cap)
- full_name
- skills (JSON array for Hub Caps)
- is_active
- created_at
- updated_at
```

#### Jobs
```sql
- id (UUID)
- job_number (unique)
- title
- description
- customer
- priority (low | medium | high | urgent)
- status (pending | in_progress | review | completed | cancelled)
- deadline
- created_by (FK to Users)
- assigned_to (FK to Users, nullable)
- files (JSON array of file references)
- metadata (JSON)
- created_at
- updated_at
- completed_at
```

#### Tasks
```sql
- id (UUID)
- job_id (FK to Jobs)
- title
- description
- type (programming | setup | machining | inspection | other)
- status (pending | assigned | in_progress | blocked | review | completed)
- priority
- assigned_to (FK to Users, nullable)
- estimated_hours
- actual_hours
- dependencies (JSON array of task IDs)
- blockers (text, nullable)
- files (JSON array)
- created_at
- updated_at
- completed_at
```

#### Modules
```sql
- id (UUID)
- name
- display_name
- description
- version
- status (active | inactive | error)
- config (JSON)
- last_run
- metrics (JSON)
- created_at
- updated_at
```

#### Activity Log
```sql
- id (UUID)
- entity_type (job | task | module | user)
- entity_id
- action
- user_id (FK to Users)
- details (JSON)
- created_at
```

## API Structure

### Authentication Endpoints
- POST `/api/auth/login` - User login
- POST `/api/auth/refresh` - Token refresh
- POST `/api/auth/logout` - User logout
- GET `/api/auth/me` - Current user info

### Job Management Endpoints
- GET `/api/jobs` - List jobs (with filters)
- POST `/api/jobs` - Create job
- GET `/api/jobs/{id}` - Get job details
- PATCH `/api/jobs/{id}` - Update job
- DELETE `/api/jobs/{id}` - Delete job
- POST `/api/jobs/{id}/files` - Upload files
- GET `/api/jobs/{id}/timeline` - Job activity timeline

### Task Management Endpoints
- GET `/api/tasks` - List tasks (with filters)
- POST `/api/tasks` - Create task
- GET `/api/tasks/{id}` - Get task details
- PATCH `/api/tasks/{id}` - Update task
- POST `/api/tasks/{id}/assign` - Assign task
- POST `/api/tasks/{id}/status` - Update status
- POST `/api/tasks/{id}/comments` - Add comment

### Module Management Endpoints (Hub Master only)
- GET `/api/modules` - List all modules
- GET `/api/modules/{id}` - Get module details
- POST `/api/modules/{id}/activate` - Activate module
- POST `/api/modules/{id}/deactivate` - Deactivate module
- PATCH `/api/modules/{id}/config` - Update config
- GET `/api/modules/{id}/metrics` - Get metrics

### User Management Endpoints (Hub Master only)
- GET `/api/users` - List users
- POST `/api/users` - Create user
- GET `/api/users/{id}` - Get user details
- PATCH `/api/users/{id}` - Update user
- DELETE `/api/users/{id}` - Deactivate user

### Analytics Endpoints
- GET `/api/analytics/dashboard` - Dashboard metrics
- GET `/api/analytics/production` - Production metrics
- GET `/api/analytics/team` - Team performance
- GET `/api/analytics/modules` - Module effectiveness

### WebSocket Endpoints
- WS `/ws/jobs` - Job updates
- WS `/ws/tasks` - Task updates
- WS `/ws/notifications` - User notifications

## Frontend Structure

### Pages

#### Hub Master Dashboard
- System overview metrics
- Active jobs summary
- Team workload visualization
- Module status cards
- Recent activity feed
- Quick actions panel

#### Hub Master Module Management
- Module grid with status indicators
- Configuration panels
- Deployment controls
- Performance metrics
- Logs and diagnostics

#### Hub Master User Management
- User list with roles
- Skill matrix
- Workload distribution
- User creation/editing

#### Hub Caps Dashboard
- My tasks queue
- Active jobs
- Team activity
- Notifications
- Quick status updates

#### Hub Caps Task View
- Task details
- File viewer/uploader
- Comments/collaboration
- Status controls
- Time tracking

#### Job Board (Shared)
- Kanban or list view
- Drag-and-drop (Hub Master)
- Filters and search
- Real-time updates

## Module Plugin System

### Base Module Interface
All modules must implement:
```python
class BaseModule:
    def __init__(self, config: dict)
    def activate(self) -> bool
    def deactivate(self) -> bool
    def process(self, data: dict) -> dict
    def get_status(self) -> dict
    def get_metrics(self) -> dict
    def health_check(self) -> bool
```

### Module Registration
Modules are discovered automatically from the `modules/` directory and registered in the database.

### Module Communication
- Modules can listen to system events
- Modules can publish events
- Modules can be triggered manually or automatically
- Inter-module communication via event bus

## Security

### Authentication Flow
1. User submits credentials
2. Server validates and returns JWT access token + refresh token
3. Client stores tokens securely
4. Access token included in API requests
5. Refresh token used to get new access token
6. Tokens expire and require re-authentication

### Authorization
- Role-based access control (Hub Master vs Hub Caps)
- Endpoint-level permissions
- Resource-level permissions (own tasks, assigned jobs)
- Audit logging for sensitive operations

### Data Security
- Passwords hashed with bcrypt
- SQL injection prevention via ORM
- XSS prevention via React
- CSRF protection
- HTTPS in production
- Secure file upload validation

## Deployment

### Development
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Production
- Docker containerization
- Docker Compose for multi-container orchestration
- Nginx reverse proxy
- PostgreSQL in separate container
- Environment-based configuration
- Automated backups

## Future Enhancements

1. **Mobile App** - React Native for on-the-floor access
2. **Machine Integration** - Direct machine status reporting
3. **AI Suggestions** - ML-based task assignment optimization
4. **Voice Commands** - Hands-free status updates
5. **AR Viewer** - 3D model visualization
6. **Advanced Analytics** - Predictive analytics for bottlenecks
7. **API Gateway** - For third-party integrations
8. **Multi-shop Support** - Multiple production facilities

## Development Principles

1. **Modularity** - Each component should be independently testable
2. **Extensibility** - Easy to add new modules and features
3. **User-Centric** - UI should be intuitive and role-appropriate
4. **Real-time** - Updates should be immediate via WebSockets
5. **Performance** - Fast load times and smooth interactions
6. **Reliability** - Graceful error handling and recovery
7. **Security** - Defense in depth, principle of least privilege
8. **Documentation** - Clear docs for users and developers

---

**The Hub** - Where production happens, monitored, optimized, and completed.
