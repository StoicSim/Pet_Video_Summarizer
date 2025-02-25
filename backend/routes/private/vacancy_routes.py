
from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date

from models import Vacancy, Leave, Employee
from enums import LeaveStatus, EmploymentStatus
from base import SessionLocal

router = APIRouter(
    prefix="/vacancies",
    tags=["vacancies"]
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
        "vacancies/list.html",
        {"request": request, "vacancies": vacancies}
    )


@router.get("/create", response_class=HTMLResponse)
async def create_position_form(request: Request):
    return templates.TemplateResponse(
        "vacancies/create.html",
        {"request": request}
    )

@router.post("/create")
async def create_vacancy(
    request: Request,
    department_id: int = Form(...),
    position_id: int = Form(...),
    position_title: str = Form(...),
    job_description: str = Form(...),
    required_skills: str = Form(...),
    open_date: date = Form(...),
    is_open: bool = Form(True),
    db: Session = Depends(get_db)
):
    vacancy = Vacancy(
        department_id=department_id,
        position_id=position_id,
        position_title=position_title,
        job_description=job_description,
        required_skills=required_skills,
        open_date=open_date,
        is_open=is_open
    )
    db.add(vacancy)
    db.commit()
    return RedirectResponse(url="/vacancies", status_code=303)

@router.post("/{vacancy_id}/delete")
async def delete_position(vacancy_id: int, db: Session = Depends(get_db)):
    id = db.query(Vacancy).filter(Vacancy.vacancy_id == vacancy_id).first()
    if id is None:
        raise HTTPException(status_code=404, detail="Position not found")
    db.delete(id)
    db.commit()
    return RedirectResponse(url="/vacancies", status_code=303)
