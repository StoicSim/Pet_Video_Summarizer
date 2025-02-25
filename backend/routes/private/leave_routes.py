from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date

from models import Leave, Employee
from enums import LeaveStatus, EmploymentStatus
from base import SessionLocal

router = APIRouter(
    prefix="/leaves",
    tags=["leaves"]
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
async def list_leaves(request: Request, db: Session = Depends(get_db)):
    leaves = db.query(Leave).all()
    return templates.TemplateResponse(
        "leaves/list.html",
        {"request": request, "leaves": leaves}
    )

@router.get("/create", response_class=HTMLResponse)
async def create_leave_form(request: Request, db: Session = Depends(get_db)):
    employees = db.query(Employee).all()
    return templates.TemplateResponse(
        "leaves/create.html",
        {"request": request, "employees": employees}
    )

@router.post("/create")
async def create_leave(
    request: Request,
    employee_id: int = Form(...),
    start_date: date = Form(...),
    end_date: date = Form(...),
    is_paid: bool = Form(...),
    status: LeaveStatus = Form(...),
    purpose: str = Form(...),
    db: Session = Depends(get_db)
):
    leave = Leave(
        employee_id=employee_id,
        start_date=start_date,
        end_date=end_date,
        is_paid=is_paid,
        status=status,
        purpose=purpose
    )

    db.add(leave)

    today = date.today()
    if (status == 'Approved' and 
        start_date <= today <= end_date):
        
        employee = db.query(Employee).filter(
            Employee.employee_id == employee_id
        ).first()
        
        if employee:
            other_active_leaves = db.query(Leave).filter(
                Leave.employee_id == employee_id,
                Leave.status == 'Approved',
                Leave.start_date <= today,
                Leave.end_date >= today,
                Leave.leave_id != leave.leave_id
            ).first()
            
            if not other_active_leaves:
                employee.employment_status = EmploymentStatus.On_Leave

    db.commit()
    return RedirectResponse(url="/leaves", status_code=303)