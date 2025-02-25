
from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date

from models import Vacancy, Leave, Employee,Applicant
from enums import LeaveStatus, EmploymentStatus
from base import SessionLocal

router = APIRouter(
    prefix="/applicants",
    tags=["applicants"]
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
async def list_applicants(request: Request, db: Session = Depends(get_db)):
    applicants = db.query(Applicant).all()
    return templates.TemplateResponse(
        "applicants/list.html",
        {"request": request, "applicants": applicants}
    )


@router.get("/create", response_class=HTMLResponse)
async def list_applicants(request: Request, db: Session = Depends(get_db)):
    applicants = db.query(Applicant).all()
    return templates.TemplateResponse(
        "applicants/create.html",
        {"request": request, "applicants": applicants}
    )
@router.post("/create")
async def create_applicant(
    request: Request,
    full_name: str = Form(...),
    contact_number: str = Form(...),
    email: str = Form(...),
    vacancy_id: int = Form(...),
    resume_url: str = Form(...),
    db: Session = Depends(get_db)
):
    applicant = Applicant(
        full_name=full_name,
        contact_number=contact_number,
        email=email,
        vacancy_id=vacancy_id,
        status="Pending",
        resume_url=resume_url,
        application_date=date.today()
    )
    db.add(applicant)
    db.commit()
    return RedirectResponse(url="/applicants", status_code=303)
