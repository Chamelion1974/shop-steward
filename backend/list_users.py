"""
Script to list all users in the database.
"""
import sys
import os

# Add the backend directory to Python path and change to backend directory
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

from app.database import SessionLocal
from app.models.user import User

def list_all_users():
    """List all users in the database"""
    db = SessionLocal()
    
    try:
        users = db.query(User).all()
        
        if users:
            print("📋 All users in database:")
            print("-" * 80)
            for user in users:
                print(f"Username: {user.username}")
                print(f"  Role: {user.role}")
                print(f"  Email: {user.email}")
                print(f"  Full Name: {user.full_name}")
                print(f"  Active: {user.is_active}")
                print(f"  ID: {user.id}")
                print("-" * 80)
            print(f"\nTotal users: {len(users)}")
        else:
            print("❌ No users found in database!")
    
    except Exception as e:
        print(f"❌ Error listing users: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    list_all_users()
