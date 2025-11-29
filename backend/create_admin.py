import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import User
from passlib.context import CryptContext

def create_admin():
    # Create database session
    db = SessionLocal()
    
    # Setup password hashing
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    # Check if admin exists
    existing_admin = db.query(User).filter(User.username == "admin").first()
    
    if existing_admin:
        print(f"Admin already exists: {existing_admin.username} ({existing_admin.email})")
    else:
        # Create admin user
        admin = User(
            username="admin",
            email="camprocsol@gmail.com",
            hashed_password=pwd_context.hash("admin123"),
            full_name="Hub Master",
            role="HUB_MASTER",
            is_active=True
        )
        db.add(admin)
        db.commit()
        print("✅ Admin user created!")
        print("   Username: admin")
        print("   Password: admin123")
        print("   Email: camprocsol@gmail.com")
    
    db.close()

if __name__ == "__main__":
    create_admin()