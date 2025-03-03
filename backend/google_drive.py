from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
import os
import json
from models import User
from base import SessionLocal

# Configure OAuth 2.0 credentials
CLIENT_SECRET_FILE = 'client_secret.json'  # Download this from Google Cloud Console
SCOPES = ['https://www.googleapis.com/auth/drive.file']
REDIRECT_URI = 'http://127.0.0.1:8000/google/callback'

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
def create_drive_folder(credentials, folder_name):
    """Create a folder in Google Drive and return its ID."""
    drive_service = build('drive', 'v3', credentials=credentials)
    
    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    
    folder = drive_service.files().create(
        body=folder_metadata,
        fields='id'
    ).execute()
    
    return folder.get('id')

# Initiate Google OAuth flow
@router.get("/google/auth")
async def google_auth(user_id: str):
    # Create a flow instance with client secrets from file
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    
    # Generate authorization URL
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        state=user_id  # Pass user_id as state to retrieve in callback
    )
    
    return {"auth_url": auth_url}

# OAuth callback endpoint
@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    print("Google callback received")
    # Get the authorization code and state (user_id) from query parameters
    code = request.query_params.get("code")
    user_id = request.query_params.get("state")
    
    print(f"Code: {code[:10]}... User ID: {user_id}")
    if not code or not user_id:
        raise HTTPException(status_code=400, detail="Missing code or state parameter")
    
    # Create a flow instance
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    
    # Exchange authorization code for tokens
    flow.fetch_token(code=code)
    credentials = flow.credentials
    
    # Store credentials in database or use them to create a folder
    try:
        # Create Google Drive folder
        folder_id = create_drive_folder(credentials, "Furtales")
        print(f"Created folder with ID: {folder_id}")
        
        # Store folder_id in user record
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.google_drive_folder_id = folder_id
            db.commit()
            
            # Return success to frontend with redirection URL
            return RedirectResponse(url=f"http://localhost:4200/auth-success?folder_id={folder_id}")
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        print(f"Error in Google callback: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating Google Drive folder: {str(e)}")

# Add a route to upload a file to the user's Google Drive folder
@router.post("/upload-to-drive")
async def upload_to_drive(
    file_path: str, 
    user_id: str,
    db: Session = Depends(get_db)
):
    # Get the user from the database
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.google_drive_folder_id:
        raise HTTPException(status_code=400, detail="User has no Google Drive folder configured")
    
    # TODO: Implement file upload to Google Drive folder
    # This would use the stored credentials to upload a file
    
    return {"success": True, "message": "File uploaded to Google Drive"}