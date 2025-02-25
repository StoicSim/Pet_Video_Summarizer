from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date

from models import Vacancy, Leave, Employee
from enums import LeaveStatus, EmploymentStatus
from base import SessionLocal

router = APIRouter(
    prefix="/job_listing",
    tags=["job_listing"]
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
async def list_vacancies(request: Request, db: Session = Depends(get_db)):
    vacancies = db.query(Vacancy).all()
    return templates.TemplateResponse(
        "public/job_listing.html",
        {"request": request, "vacancies": vacancies}
    )