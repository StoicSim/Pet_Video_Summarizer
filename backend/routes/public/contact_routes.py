from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date
import json

from models import ContactUs

from base import SessionLocal

router = APIRouter(
    prefix="/contact",
    tags=["contact"]
)

templates = Jinja2Templates(directory="templates")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("public/contact.html", {"request": request})

@router.post("/")
async def create_position(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),    
    subject: str = Form(...),
    message: str = Form(...),
    phone:str=Form(None),
    db: Session = Depends(get_db)
):
    try:
        contact_us = ContactUs(
            username=username,
            email=email,
            phone=phone,
            subject=subject,
            message=message,
        )
        db.add(contact_us)
        db.commit()
        return RedirectResponse(url="/contact", status_code=303)
    except Exception as e:
        db.rollback()
        # In a production environment, you should log the error
        return {"error": str(e)}, 500