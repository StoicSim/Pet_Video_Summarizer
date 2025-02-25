
from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date

from models import Payment
from enums import LeaveStatus, EmploymentStatus
from base import SessionLocal

router = APIRouter(
    prefix="/payments",
    tags=["payments"]
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
async def list_payments(request: Request, db: Session = Depends(get_db)):
    payments = db.query(Payment).all()
    return templates.TemplateResponse(
        "payments/list.html",
        {"request": request, "payments": payments}
    )

@router.post("/create")
async def create_payment(
    request: Request,
    employee_id: int = Form(...),
    pending_salary: float = Form(...),
    last_payment_date: date = Form(...),
    appraisal_date: date = Form(...),
    adjustments: float = Form(0.0),
    db: Session = Depends(get_db)
):
    payment = Payment(
        employee_id=employee_id,
        pending_salary=pending_salary,
        last_payment_date=last_payment_date,
        appraisal_date=appraisal_date,
        adjustments=adjustments
    )
    db.add(payment)
    db.commit()
    return RedirectResponse(url="/payments", status_code=303)