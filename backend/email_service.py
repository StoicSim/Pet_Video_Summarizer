from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from fastapi import BackgroundTasks
from pydantic import EmailStr
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Email configuration
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM", "noreply@furtales.com"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME", "Furtales"),
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

async def send_video_upload_notification(email: EmailStr, video_id: str, drive_link: str):
    """
    Send notification email when a video has been processed and uploaded to Google Drive
    """
    message = MessageSchema(
        subject="Your Furtales Video is Ready!",
        recipients=[email],
        body=f"""
        <html>
        <body>
            <h1>Your pet video has been processed!</h1>
            <p>Good news! We've finished processing your video and uploaded it to your Google Drive.</p>
            <p>Video ID: {video_id}</p>
            <p>You can view your video here: <a href="{drive_link}">View on Google Drive</a></p>
            <p>Thank you for using Furtales!</p>
        </body>
        </html>
        """,
        subtype="html"
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)
    
async def send_welcome_email(email: EmailStr, username: str):
    """
    Send welcome email after a user registers
    """
    message = MessageSchema(
        subject="Welcome to Furtales!",
        recipients=[email],
        body=f"""
        <html>
        <body>
            <h1>Welcome to Furtales, {username}!</h1>
            <p>Thank you for registering with Furtales. We're excited to help you create amazing pet video summaries.</p>
            <p>To get started, upload your first pet video and we'll process it for you.</p>
            <p>Best regards,<br>The Furtales Team</p>
        </body>
        </html>
        """,
        subtype="html"
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)