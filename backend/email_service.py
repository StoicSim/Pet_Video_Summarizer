import os
import requests
import json
import asyncio
from dotenv import load_dotenv

load_dotenv()

def send_welcome_email(to_email: str, username: str):
    """
    Send a welcome email to a new user using SendGrid
    """
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
    if not SENDGRID_API_KEY:
        print("SendGrid API key not found")
        return

    url = "https://api.sendgrid.com/v3/mail/send"
    
    headers = {
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json"
    }

    content = f"""
    Welcome to Furtales, {username}!

    We're excited to have you join our platform. Get ready to create amazing video summaries of your beloved pets.

    Here's what you can do:
    - Upload videos of your pets
    - Get AI-generated summaries
    - Store and share memories

    Let's make every pet moment memorable!

    Best regards,
    The Furtales Team
    """

    data = {
        "personalizations": [
            {
                "to": [{"email": to_email}],
                "subject": "Welcome to Furtales!"
            }
        ],
        "from": {
            "email": "078bct089.simran@pcampus.edu.np",
            "name": "Furtales Team"
        },
        "content": [
            {
                "type": "text/plain",
                "value": content
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 202:
            print(f"Welcome email sent successfully to {to_email}")
        else:
            print(f"Failed to send welcome email. Status code: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error sending welcome email: {e}")

async def send_video_upload_notification(to_email: str, video_id: str, video_link: str = None):
    """
    Send a video upload notification email using SendGrid
    
    Args:
        to_email (str): Recipient's email address
        video_id (str): Unique identifier for the video
        video_link (str, optional): Link to the processed video
    """
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
    if not SENDGRID_API_KEY:
        print("SendGrid API key not found")
        return

    url = "https://api.sendgrid.com/v3/mail/send"
    
    headers = {
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json"
    }

    # Prepare content based on whether video link is available
    if video_link:
        content = f"""
        Great news! Your video summary is ready.

        Video ID: {video_id}
        You can view your processed video here: {video_link}

        Enjoy your pet's memorable moments!

        Best regards,
        The Furtales Team
        """
        subject = "Your Video Summary is Ready!"
    else:
        content = f"""
        Your video (ID: {video_id}) is being processed.

        We'll notify you once it's complete.

        Best regards,
        The Furtales Team
        """
        subject = "Video Processing Started"

    data = {
        "personalizations": [
            {
                "to": [{"email": to_email}],
                "subject": subject
            }
        ],
        "from": {
            "email": "078bct089.simran@pcampus.edu.np",
            "name": "Furtales Team"
        },
        "content": [
            {
                "type": "text/plain",
                "value": content
            }
        ]
    }

    try:
        # Use requests in an async-safe way with asyncio
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, 
            lambda: requests.post(url, headers=headers, json=data)
        )
        
        if response.status_code == 202:
            print(f"Video notification email sent successfully to {to_email}")
        else:
            print(f"Failed to send video notification email. Status code: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error sending video upload notification: {e}")