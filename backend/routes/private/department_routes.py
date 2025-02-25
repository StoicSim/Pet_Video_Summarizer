from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from models import Department
from base import SessionLocal

router = APIRouter(
    prefix="/departments",
    tags=["departments"]
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
async def list_departments(request: Request, db: Session = Depends(get_db)):
    departments = db.query(Department).all()
    return templates.TemplateResponse(
        "departments/list.html",
        {"request": request, "departments": departments}
    )

@router.get("/create", response_class=HTMLResponse)
async def create_department_form(request: Request):
    return templates.TemplateResponse(
        "departments/create.html",
        {"request": request}
    )

@router.post("/create")
async def create_department(
    request: Request,
    department_name: str = Form(...),
    hod_id: int = Form(...),
    dhod_id: int = Form(...),
    contact_number: str = Form(...),
    db: Session = Depends(get_db)
):
    department = Department(
        department_name=department_name,
        hod_id=hod_id,
        dhod_id=dhod_id,
        contact_number=contact_number
    )
    db.add(department)
    db.commit()
    return RedirectResponse(url="/departments", status_code=303)

@router.get("/{department_id}", response_class=HTMLResponse)
async def read_department(request: Request, department_id: int, db: Session = Depends(get_db)):
    department = db.query(Department).filter(Department.department_id == department_id).first()
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    return templates.TemplateResponse(
        "departments/detail.html",
        {"request": request, "department": department}
    )

@router.get("/{department_id}/edit", response_class=HTMLResponse)
async def edit_department_form(request: Request, department_id: int, db: Session = Depends(get_db)):
    department = db.query(Department).filter(Department.department_id == department_id).first()
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    return templates.TemplateResponse(
        "departments/edit.html",
        {"request": request, "department": department}
    )

@router.post("/{department_id}/edit")
async def edit_department(
    request: Request,
    department_id: int,
    department_name: str = Form(...),
    hod_id: int = Form(...),
    dhod_id: int = Form(...),
    contact_number: str = Form(...),
    db: Session = Depends(get_db)
):
    department = db.query(Department).filter(Department.department_id == department_id).first()
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    
    department.department_name = department_name
    department.hod_id = hod_id
    department.dhod_id = dhod_id
    department.contact_number = contact_number
    
    db.commit()
    return RedirectResponse(url=f"/departments/{department_id}", status_code=303)

@router.post("/{department_id}/delete")
async def delete_department(department_id: int, db: Session = Depends(get_db)):
    department = db.query(Department).filter(Department.department_id == department_id).first()
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    db.delete(department)
    db.commit()
    return RedirectResponse(url="/departments", status_code=303)