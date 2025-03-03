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
import random
from googleapiclient.http import MediaFileUpload
from models import Video

SAMPLE_VIDEOS_FOLDER = 'sample'  # Folder containing sample videos


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
def get_drive_service(user_id: str):
    try:
        token_path = f'tokens/{user_id}.json'
        if not os.path.exists(token_path):
            return None
        
        with open(token_path, 'r') as token_file:
            token_data = json.load(token_file)
        
        credentials = Credentials(
            token=token_data['token'],
            refresh_token=token_data['refresh_token'],
            token_uri=token_data['token_uri'],
            client_id=token_data['client_id'],
            client_secret=token_data['client_secret'],
            scopes=token_data['scopes']
        )
        
        return build('drive', 'v3', credentials=credentials)
    
    except Exception as e:
        print(f"Error getting Drive service: {e}")
        return None
def upload_sample_video_to_drive(user_id: str, video_id: str, db: Session):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"User {user_id} not found")
            return None
        
        if not user.google_drive_folder_id:
            print(f"User {user_id} has no Google Drive folder ID")
            return None
        
        video = db.query(Video).filter(Video.unique_id == video_id).first()
        if not video:
            print(f"Video {video_id} not found")
            return None
        
        drive_service = get_drive_service(user_id)
        if not drive_service:
            print(f"Could not get Drive service for user {user_id}. Check if token file exists.")
            return None
        
        # Check if sample folder exists
        if not os.path.exists(SAMPLE_VIDEOS_FOLDER):
            print(f"Sample videos folder '{SAMPLE_VIDEOS_FOLDER}' does not exist")
            return None
        
        sample_videos = [f for f in os.listdir(SAMPLE_VIDEOS_FOLDER) if f.endswith(('.mp4', '.mov', '.avi'))]
        if not sample_videos:
            print("No sample videos found in the sample folder")
            return None
        
        sample_video = random.choice(sample_videos)
        sample_video_path = os.path.join(SAMPLE_VIDEOS_FOLDER, sample_video)
        
        # Check if the sample video file exists
        if not os.path.exists(sample_video_path):
            print(f"Sample video file '{sample_video_path}' does not exist")
            return None
        
        file_metadata = {
            'name': f'Summary_{video_id}.mp4',
            'parents': [user.google_drive_folder_id]
        }
        
        media = MediaFileUpload(sample_video_path, mimetype='video/mp4', resumable=True)
        
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id,webViewLink'
        ).execute()
        
        file_url = file.get('webViewLink')
        print(f"Successfully uploaded video to Google Drive: {file_url}")
        
        return file_url
    
    except Exception as e:
        print(f"Error uploading to Google Drive: {e}")
        import traceback
        traceback.print_exc()
        return None
      
      
def process_video_with_drive_upload(video_id: str, db_session):
    import time
    import random
    from models import Video, ProcessingStatus
    
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
        
        # Sleep for a shorter time in development (10 seconds)
        # In production, you would replace this with actual video processing
        time.sleep(10)
        
        # Generate mock data
        animal_types = ["dog", "cat", "bird", "rabbit", "hamster"]
        animal_type = random.choice(animal_types)
        
        # Update basic video info
        video.source_video_duration = random.uniform(10, 120)  # 10-120 seconds
        video.animal_type = animal_type
        
        # If user is authenticated and has Google Drive integration, upload sample video
        if video.user_id:
            summary_video_link = upload_sample_video_to_drive(video.user_id, video.unique_id, db)
            if summary_video_link:
                video.summary_video_link = summary_video_link
            else:
                # Fallback if Google Drive upload fails
                video.summary_video_link = f"https://example.com/processed/{video_id}.mp4"
        else:
            # For anonymous users, just use a mock URL
            video.summary_video_link = f"https://example.com/processed/{video_id}.mp4"
        
        # Add summary text
        video.summary_text = f"This is a {animal_type} video that shows various activities. The animal appears to be happy and playful."
        video.processing_status = ProcessingStatus.COMPLETED
        
        # Commit changes
        db.commit()
        print(f"Video {video_id} processing completed successfully")
        
    except Exception as e:
        print(f"Error processing video {video_id}: {e}")
        try:
            # Update video with error status
            video = db.query(Video).filter(Video.unique_id == video_id).first()
            if video:
                video.processing_status = ProcessingStatus.FAILED
                video.error_message = str(e)
                db.commit()
        except Exception as db_error:
            print(f"Error updating video status: {db_error}")
    finally:
        db.close()

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
    
    # Store credentials in a token file
    if not os.path.exists('tokens'):
        os.makedirs('tokens')
    
    token_data = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    
    with open(f'tokens/{user_id}.json', 'w') as token_file:
        json.dump(token_data, token_file)
    
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