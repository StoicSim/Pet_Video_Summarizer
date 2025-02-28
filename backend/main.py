from base import SessionLocal, Base, engine
from models import User, Video, ProcessingStatus
from fastapi import FastAPI, HTTPException,Path, Depends, status, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
import uuid
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime,time as datetime_time,timedelta,date
from datetime import datetime, date, time as datetime_time  # Rename to avoid conflict

from typing import Union, Optional,List
import random
import time

from sqlalchemy import text

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully.")
    except Exception as e:
        print(f"Error creating database tables: {e}")

if __name__ == "__main__":
    init_db()
    
# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    pet_name: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if username or email already exists
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = pwd_context.hash(user.password)
    new_user = User(
        id=str(uuid.uuid4()),
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        pet_name=user.pet_name
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User registered successfully", "user_id": new_user.id}

# JWT Configuration
SECRET_KEY = "your-secret-key-keep-this-very-secret"  # Change this in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    username: str

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

class LoginData(BaseModel):
    username: str
    password: str

@app.post("/login", response_model=Token)
def login(login_data: LoginData, db: Session = Depends(get_db)):
    # Find user by username
    user = db.query(User).filter(User.username == login_data.username).first()
    
    # Verify user exists and password is correct
    if not user or not pwd_context.verify(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    # Return token and user info
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username
    }

# Pydantic model for video upload
class VideoUpload(BaseModel):
    source_video_link: str
    email: Optional[str] = None

# JWT token model for auth validation
class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[str] = None

# Function to decode JWT token
def decode_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return TokenData(username=username, user_id=user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# Get current user from token
async def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="login")), db: Session = Depends(get_db)):
    token_data = decode_token(token)
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Optional auth - for endpoints that work both with and without auth
async def get_optional_user(token: str = None, db: Session = Depends(get_db)):
    if token:
        try:
            token_data = decode_token(token)
            return db.query(User).filter(User.id == token_data.user_id).first()
        except:
            return None
    return None

# Mock video processing function
def mock_process_video(video_id: str, db_session):
    try:
        print(f"Starting processing for video {video_id}")
        
        # Get the video from the database
        db = db_session()
        video = db.query(Video).filter(Video.unique_id == video_id).first()
        
        if not video:
            print(f"Video {video_id} not found")
            return
        
        # Update video with processing status
        video.processing_status = ProcessingStatus.PROCESSING
        db.commit()
        
        # Sleep for 2 minutes (120 seconds)
        time.sleep(120)
        
        # Generate mock data
        animal_types = ["dog", "cat", "bird", "rabbit", "hamster"]
        
        # Update video with completed information
        video.source_video_duration = random.uniform(10, 120)  # 10-120 seconds
        video.animal_type = random.choice(animal_types)
        video.summary_video_link = f"https://example.com/processed/{video_id}.mp4"
        video.summary_text = f"This is a {video.animal_type} video that shows various activities. The animal appears to be happy and playful."
        video.processing_status = ProcessingStatus.COMPLETED
        
        # Commit changes
        db.commit()
        print(f"Video {video_id} processing completed successfully after 2 minutes")
        
    except Exception as e:
        print(f"Error processing video {video_id}: {e}")
        try:
            # Update video with error status
            video = db.query(Video).filter(Video.unique_id == video_id).first()
            if video:
                video.processing_status = ProcessingStatus.FAILED
                video.error_message = str(e)
                db.commit()
        except:
            pass
    finally:
        db.close()

@app.post("/videos/upload", response_model=dict)
async def upload_video(
    video_data: VideoUpload,
    background_tasks: BackgroundTasks,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    # Check if the user is authenticated
    user = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        try:
            token_data = decode_token(token)
            user = db.query(User).filter(User.id == token_data.user_id).first()
        except Exception as e:
            print(f"Token validation error: {e}")
            # We don't raise an exception here, just continue as anonymous

    # If authenticated, use user info
    if user:
        print(f"Authenticated user: {user.username}")
        email = user.email
        user_id = user.id
    # If not authenticated, require email
    elif video_data.email:
        print(f"Anonymous upload with email: {video_data.email}")
        email = video_data.email
        user_id = None
    else:
        raise HTTPException(
            status_code=400,
            detail="Email is required for anonymous uploads"
        )
        
    if user:
        expiry_date = datetime.utcnow() + timedelta(days=30)  # 30 days for authenticated users
    else:
        expiry_date = datetime.utcnow() + timedelta(minutes=5) 

    # Create a new video record
    new_video = Video(
        user_id=user_id,
        email=email,
        source_video_link=video_data.source_video_link,
        processing_status=ProcessingStatus.PENDING,
        expiry_date=expiry_date
    )

    # Add and commit to database
    db.add(new_video)
    db.commit()
    db.refresh(new_video)
    
    # Trigger the mock processing in background
    background_tasks.add_task(mock_process_video, new_video.unique_id, SessionLocal)

    return {
        "message": "Video uploaded successfully. Processing started.",
        "video_id": new_video.unique_id
    }

# Endpoint to get videos for the current authenticated user
@app.get("/videos/user")
async def get_user_videos(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    videos = db.query(Video).filter(Video.user_id == current_user.id).all()
    return videos

# Endpoint to get a specific video by ID
@app.get("/videos/{video_id}")
async def get_video(video_id: str, db: Session = Depends(get_db)):
    video = db.query(Video).filter(Video.unique_id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video

# Create the OAuth2PasswordBearer instance
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)

# Update your get_current_user function
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    token_data = decode_token(token)
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user
# timeline endpoints

@app.get("/videos/today")
async def get_today_videos(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get all videos uploaded by the current user today.
    Videos are ordered by creation time (newest first).
    """
    # Get today's date range (from midnight to 11:59:59 PM)
    today = datetime.now().date()
    start_of_day = datetime.combine(today, datetime.time.min)
    end_of_day = datetime.combine(today, datetime.time.max)
    
    # Query videos created today by the current user
    today_videos = db.query(Video).filter(
        Video.user_id == current_user.id,
        Video.created_at >= start_of_day,
        Video.created_at <= end_of_day
    ).order_by(Video.created_at.desc()).all()
    
    return today_videos

#timeline for date

@app.get("/videos/date/{selected_date}")
async def get_videos_by_date(
    selected_date: str = Path(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Print the current user details from the token
        print(f"Current user from token: ID={current_user.id}, Username={current_user.username}")
        
        parsed_date = date.fromisoformat(selected_date)
        print(f"Requested date: {parsed_date}")
        
        # Check database timezone (using proper SQLAlchemy text() function)
        try:
            db_timezone = db.execute(text("SHOW timezone")).scalar()
            print(f"Database timezone: {db_timezone}")
        except Exception as tz_error:
            print(f"Unable to get database timezone: {str(tz_error)}")
        
        # First, check if this user has any videos at all
        all_videos = db.query(Video).filter(
            Video.user_id == current_user.id
        ).all()
        
        print(f"Total videos for user {current_user.id}: {len(all_videos)}")
        for v in all_videos:
            print(f"  User video: {v.unique_id}, created_at={v.created_at}")
        
        # Now try to get videos for the specific date
        start_of_day = datetime.combine(parsed_date, datetime_time.min)
        end_of_day = datetime.combine(parsed_date, datetime_time.max)
        
        print(f"Searching for videos between {start_of_day} and {end_of_day}")
        
        date_videos = db.query(Video).filter(
            Video.user_id == current_user.id,
            Video.created_at >= start_of_day,
            Video.created_at <= end_of_day
        ).order_by(Video.created_at.desc()).all()
        
        print(f"Videos for date {parsed_date}: {len(date_videos)}")
        
        # For debugging, get all videos for this date regardless of user
        all_date_videos = db.query(Video).filter(
            Video.created_at >= start_of_day,
            Video.created_at <= end_of_day
        ).all()
        
        print(f"All videos for date {parsed_date} (any user): {len(all_date_videos)}")
        for v in all_date_videos:
            print(f"  Video {v.unique_id}: user_id={v.user_id}, email={v.email}, created_at={v.created_at}")
        
        return date_videos
    except Exception as e:
        print(f"Error processing date request: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")