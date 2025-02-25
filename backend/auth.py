from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from models import User
from base import SessionLocal

# Security constants
SECRET_KEY = "your-secret-key-here"  # Change this to a secure secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(request: Request, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = request.cookies.get("access_token")
    if not token:
        raise credentials_exception
        
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# Middleware for protecting routes
# auth.py (updating only the middleware part)
# async def auth_middleware(request, call_next):
#     # Define public and private paths
#     public_paths = {"/login", "/", "/about", "/contact", 
#                    "/department_list", "/interview_dates", 
#                    "/job_listing", "/position_list", "/logout"}
    
#     private_paths = {"/dashboard", "/employees", "/departments", 
#                     "/leaves", "/positions", "/vacancies", 
#                     "/applicants", "/interviews", "/payments"}
    
#     # current_path = request.url.path.rstrip('/')
#     current_path = request.url.path.rstrip('/')

    
#     # Allow static files
#     if current_path.startswith("/static"):
#         response = await call_next(request)
#         return response
        
#     # Check if path is private
#     is_private = any(current_path.startswith(path) for path in private_paths)
#     if is_private:
#         try:
#             token = request.cookies.get("access_token")
#             if not token:
#                 # Redirect to login if no token
#                 from fastapi.responses import RedirectResponse
#                 return RedirectResponse(url="/login", status_code=302)
            
#             # Verify token
#             try:
#                 payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#                 username = payload.get("sub")
#                 if username is None:
#                     return RedirectResponse(url="/login", status_code=302)
#             except JWTError:
#                 return RedirectResponse(url="/login", status_code=302)
                
#         except Exception:
#             return RedirectResponse(url="/login", status_code=302)
    
#     response = await call_next(request)
#     return response

# auth.py
async def auth_middleware(request, call_next):
    # Define public and private paths
    public_paths = {"/login", "/", "/about", "/contact", 
                   "/department_list", "/interview_dates", 
                   "/job_listing", "/position_list", "/logout"}
    
    path = request.url.path.rstrip('/')
    
    #root path
    if path == "" or path == "/":
        response = await call_next(request)
        return response
    
    # Allow static files
    if path.startswith("/static"):
        response = await call_next(request)
        return response
    
    # Better public path checking that handles subpaths
    is_public = False
    for public_path in public_paths:
        # Check if the path exactly matches or is a subpath of a public path
        if path == public_path or path.startswith(public_path + "/"):
            is_public = True
            break
    
    if not is_public:
        token = request.cookies.get("access_token")
        if not token:
            return RedirectResponse(
                url="/login?next=" + request.url.path,
                status_code=status.HTTP_303_SEE_OTHER
            )
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if not username:
                return RedirectResponse(
                    url="/login",
                    status_code=status.HTTP_303_SEE_OTHER
                )
            
            # Add user to request state
            request.state.user = username
            
        except JWTError:
            return RedirectResponse(
                url="/login",
                status_code=status.HTTP_303_SEE_OTHER
            )
    
    response = await call_next(request)
    return response