# main.py
from base import Base, engine
from models import User, Video, ProcessingStatus  # Import models to register them

def init_db():
    try:
        # Create all tables in the database
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully.")
    except Exception as e:
        print(f"Error creating database tables: {e}")

if __name__ == "__main__":
    init_db()