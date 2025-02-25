from models import User
from base import SessionLocal
from auth1 import get_password_hash
import datetime

def create_initial_user():
    db = SessionLocal()
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("Admin user already exists")
            return
        
        admin_user = User(
            username="admin1",
            password=get_password_hash("pass"),
            is_admin=True,
            role="admin",  # Add role if your User model has this field
            created_at=datetime.datetime.utcnow(),
            last_login=None
        )
        
        db.add(admin_user)
        db.commit()
        print("Admin user created successfully")
    except Exception as e:
        print(f"Error creating admin user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_initial_user()