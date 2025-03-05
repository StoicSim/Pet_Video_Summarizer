# models.py
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from base import Base
import uuid

class ProcessingStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    pet_name = Column(String(50), nullable=False)
    streak = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_active_date = Column(DateTime(timezone=True), server_default=func.now())
    google_drive_folder_id = Column(String(255), nullable=True)  # New field
    
    # Relationships
    videos = relationship("Video", back_populates="user")
class Video(Base):
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    unique_id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, index=True)
    
    # Only link to user table for registered users
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    # Store email for both anonymous and registered users
    email = Column(String(100), index=True)
    
    source_video_link = Column(String(255))
    source_video_duration = Column(Float, nullable=True)  # In seconds
    animal_type = Column(String(50), index=True,nullable=True)  # Changed to String
    
    summary_video_link = Column(String(255), nullable=True)
    summary_text = Column(Text, nullable=True)
    
    processing_status = Column(Enum(ProcessingStatus), default=ProcessingStatus.PENDING)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expiry_date = Column(DateTime(timezone=True), nullable=True)  # When to delete data
    
    # Relationships
    user = relationship("User", back_populates="videos")