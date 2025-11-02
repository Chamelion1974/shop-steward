"""
API routes for The Hub.
"""
from fastapi import APIRouter
from .auth import router as auth_router
from .jobs import router as jobs_router
from .tasks import router as tasks_router
from .users import router as users_router
from .modules import router as modules_router


# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(jobs_router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(tasks_router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(modules_router, prefix="/modules", tags=["Modules"])
