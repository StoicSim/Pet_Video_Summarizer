# main.py

#database creation imports
from base import SessionLocal,Base, engine
from models import User, Video, ProcessingStatus  # Import models to register them

#api setup imports
from fastapi import FastAPI, HTTPException, Depends, HTTPException, status,Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
import uuid
from passlib.context import CryptContext


from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Union,Optional




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
        # Create all tables in the database
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

#login endpoints


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
    
#video url end points



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
async def get_current_user(token: str = Depends(OAuth2PasswordBearer    (tokenUrl="login")), db: Session = Depends(get_db)):
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


@app.post("/videos/upload", response_model=dict)
async def upload_video(
    video_data: VideoUpload,
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

    # Create a new video record
    new_video = Video(
        user_id=user_id,
        email=email,
        source_video_link=video_data.source_video_link,
        processing_status=ProcessingStatus.PENDING,
        # Set expiry date (e.g., 30 days from now)
        expiry_date=datetime.utcnow() + timedelta(days=30)
    )

    # Add and commit to database
    db.add(new_video)
    db.commit()
    db.refresh(new_video)

    return {
        "message": "Video uploaded successfully",
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