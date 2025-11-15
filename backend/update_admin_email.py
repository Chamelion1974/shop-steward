"""
Script to update the admin user's email in the database.
"""
import sys
import os

# Add the backend directory to Python path and change to backend directory
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

from app.database import SessionLocal
from app.models.user import User

def update_admin_email():
    """Update the admin user's email to camprocsol@gmail.com"""
    db = SessionLocal()
    
    try:
        # Find the admin user
        admin = db.query(User).filter(User.username == "admin").first()
        
        if admin:
            old_email = admin.email
            admin.email = "camprocsol@gmail.com"
            db.commit()
            print("✅ Admin email updated!")
            print(f"   Old email: {old_email}")
            print(f"   New email: {admin.email}")
            print(f"   Username: {admin.username}")
        else:
            print("❌ Admin user not found!")
            print("   Try running create_admin.py first")
    
    except Exception as e:
        print(f"❌ Error updating admin email: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_admin_email()
