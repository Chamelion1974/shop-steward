"""
Script to upgrade a user to Hub Master role.
"""
import sys
import os

# Add the backend directory to Python path and change to backend directory
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

from app.database import SessionLocal
from app.models.user import User, UserRole

def upgrade_to_hub_master(username: str = "admin"):
    """Upgrade a user to Hub Master role"""
    db = SessionLocal()
    
    try:
        # Find the user
        user = db.query(User).filter(User.username == username).first()
        
        if user:
            old_role = user.role
            user.role = UserRole.HUB_MASTER
            db.commit()
            print("✅ User role updated!")
            print(f"   Username: {user.username}")
            print(f"   Old role: {old_role}")
            print(f"   New role: {user.role}")
            print(f"   Email: {user.email}")
        else:
            print(f"❌ User '{username}' not found!")
            print("   Available users:")
            users = db.query(User).all()
            for u in users:
                print(f"   - {u.username} ({u.role})")
    
    except Exception as e:
        print(f"❌ Error updating user role: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Get username from command line or use default
    username = sys.argv[1] if len(sys.argv) > 1 else "admin"
    upgrade_to_hub_master(username)
