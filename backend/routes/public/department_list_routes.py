from fastapi import APIRouter, Request, Depends,HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from models import Department
from base import SessionLocal
from sqlalchemy.orm import joinedload


router = APIRouter(
    prefix="/department_list",  # Changed from departments_public to match URL conventions
    tags=["department_list"]
)

templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_class=HTMLResponse)
async def list_public_departments(request: Request, db: Session = Depends(get_db)):
    # Query only departments (not employees as in your original code)
    departments = db.query(Department).all()
    return templates.TemplateResponse(
        "public/department_list.html",  # Changed template path
        {"request": request, "departments": departments}
    )


