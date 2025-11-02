"""
Main FastAPI application for The Hub.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .database import engine, Base
from .api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    print("🚀 Starting The Hub...")

    # Create database tables
    print("📊 Creating database tables...")
    Base.metadata.create_all(bind=engine)

    # Initialize default admin user if none exists
    from .database import SessionLocal
    from .models.user import User, UserRole
    from .core.security import get_password_hash
    import uuid

    db = SessionLocal()
    try:
        admin_count = db.query(User).filter(User.role == UserRole.HUB_MASTER).count()
        if admin_count == 0:
            print("👤 Creating default admin user...")
            admin = User(
                id=str(uuid.uuid4()),
                username="admin",
                email="admin@shopsteward.local",
                full_name="Hub Master",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.HUB_MASTER,
                skills=[]
            )
            db.add(admin)
            db.commit()
            print("✅ Default admin created (username: admin, password: admin123)")
            print("⚠️  Please change the default password immediately!")
    finally:
        db.close()

    print("✨ The Hub is ready!")

    yield

    # Shutdown
    print("👋 Shutting down The Hub...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": "/api/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
