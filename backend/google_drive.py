from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
import os
import json
import random
import uuid
from models import User, Video, ProcessingStatus
from base import SessionLocal
from googleapiclient.http import MediaFileUpload
from email_service import send_video_upload_notification
from final import process_video, download_youtube_video_480p, download_from_gdrive

SAMPLE_VIDEOS_FOLDER = 'sample'
CLIENT_SECRET_FILE = 'client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/drive.file']
REDIRECT_URI = 'http://127.0.0.1:8000/google/callback'

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

def create_drive_folder(credentials, folder_name):
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
# ... (rest of the code remains the same)

def process_and_upload_video(video_id: str, video_link: str, user_id: str, db: Session, background_tasks: BackgroundTasks = None):
    try:
        video = db.query(Video).filter(Video.unique_id == video_id).first()
        if not video:
            print(f"Video {video_id} not found")
            return None
        
        if "youtube.com" in video_link or "youtu.be" in video_link:
            input_video = download_youtube_video_480p(video_link)
        elif "drive.google.com" in video_link:
            input_video = download_from_gdrive(video_link, f"{video_id}_input.mp4")
        else:
            input_video = video_link
        
        output_video = f"processed_{video_id}.mp4"
        
        processing_result = process_video(
            input_video, 
            output_video, 
            chunk_duration=900,
            max_clips=10,
            background_tasks=background_tasks
        )
        
        # ... (rest of the function remains the same)

# ... (rest of the code remains the same)

        
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.google_drive_folder_id:
            drive_service = get_drive_service(user_id)
            
            if drive_service:
                file_metadata = {
                    'name': f'Summary_{video_id}.mp4',
                    'parents': [user.google_drive_folder_id]
                }
                
                media = MediaFileUpload(output_video, mimetype='video/mp4', resumable=True)
                
                file = drive_service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id,webViewLink'
                ).execute()
                
                summary_video_link = file.get('webViewLink')
                
                video.summary_video_link = summary_video_link
                video.summary_text = processing_result.get('overall_summary', '')
                video.processing_status = ProcessingStatus.COMPLETED
                
                if background_tasks and user.email:
                    background_tasks.add_task(
                        send_video_upload_notification, 
                        user.email, 
                        video_id, 
                        summary_video_link
                    )
                
                db.commit()
                return summary_video_link
        
        video.summary_video_link = output_video
        video.summary_text = processing_result.get('overall_summary', '')
        video.processing_status = ProcessingStatus.COMPLETED
        db.commit()
        
        return output_video
    
    except Exception as e:
        print(f"Error in video processing and upload: {e}")
        try:
            video = db.query(Video).filter(Video.unique_id == video_id).first()
            if video:
                video.processing_status = ProcessingStatus.FAILED
                video.error_message = str(e)
                db.commit()
        except Exception as db_error:
            print(f"Error updating video status: {db_error}")
        
        return None

def process_video_with_drive_upload(video_id: str, db_session, background_tasks: BackgroundTasks = None):
    try:
        print(f"Starting processing for video {video_id}")
        
        db = db_session()
        video = db.query(Video).filter(Video.unique_id == video_id).first()
        
        if not video:
            print(f"Video {video_id} not found")
            return
        
        video.processing_status = ProcessingStatus.PROCESSING
        db.commit()
        
        summary_video_link = process_and_upload_video(
            video_id,
            video.source_video_link,
            video.user_id,
            db,
            background_tasks
        )
        
        if summary_video_link:
            print(f"Video {video_id} processing completed successfully")
        else:
            print(f"Video {video_id} processing failed")
        
    except Exception as e:
        print(f"Error processing video {video_id}: {e}")
        try:
            video = db.query(Video).filter(Video.unique_id == video_id).first()
            if video:
                video.processing_status = ProcessingStatus.FAILED
                video.error_message = str(e)
                db.commit()
        except Exception as db_error:
            print(f"Error updating video status: {db_error}")
    finally:
        db.close()

@router.get("/google/auth")
async def google_auth(user_id: str):
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        state=user_id
    )
    
    return {"auth_url": auth_url}

@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    print("Google callback received")
    code = request.query_params.get("code")
    user_id = request.query_params.get("state")
    
    print(f"Code: {code[:10]}... User ID: {user_id}")
    if not code or not user_id:
        raise HTTPException(status_code=400, detail="Missing code or state parameter")
    
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    
    flow.fetch_token(code=code)
    credentials = flow.credentials
    
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
    
    try:
        folder_id = create_drive_folder(credentials, "Furtales")
        print(f"Created folder with ID: {folder_id}")
        
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.google_drive_folder_id = folder_id
            db.commit()
            
            return RedirectResponse(url=f"http://localhost:4200/auth-success?folder_id={folder_id}")
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        print(f"Error in Google callback: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating Google Drive folder: {str(e)}")

@router.post("/process-video")
async def trigger_video_processing(
    video_link: str, 
    user_id: str, 
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    try:
        video = Video(
            unique_id=str(uuid.uuid4()),
            user_id=user_id,
            original_video_link=video_link,
            processing_status=ProcessingStatus.PENDING
        )
        db.add(video)
        db.commit()
        
        background_tasks.add_task(
            process_and_upload_video, 
            video.unique_id, 
            video_link, 
            user_id, 
            db, 
            background_tasks
        )
        
        return {
            "message": "Video processing started", 
            "video_id": video.unique_id
        }
    
    except Exception as e:
        print(f"Error initiating video processing: {e}")
        return JSONResponse(
            status_code=500, 
            content={"error": "Failed to start video processing"}
        )
