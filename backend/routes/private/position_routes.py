from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from models import Position
from base import SessionLocal

router = APIRouter(
    prefix="/positions",
    tags=["positions"]
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
async def list_positions(request: Request, db: Session = Depends(get_db)):
    positions = db.query(Position).all()
    return templates.TemplateResponse(
        "positions/list.html",
        {"request": request, "positions": positions}
    )

@router.get("/create", response_class=HTMLResponse)
async def create_position_form(request: Request):
    return templates.TemplateResponse(
        "positions/create.html",
        {"request": request}
    )

@router.post("/create")
async def create_position(
    request: Request,
    title: str = Form(...),
    base_salary_full: float = Form(...),
    department_id: int = Form(...),
    base_salary_part: float = Form(...),
    allowances: float = Form(...),
    description: str = Form(...),
    required_skills: str = Form(...),
    db: Session = Depends(get_db)
):
    position = Position(
        title=title,
        base_salary_full=base_salary_full,
        base_salary_part=base_salary_part,
        allowances=allowances,
        description=description,
        department_id=department_id,
        required_skills=required_skills
    )
    db.add(position)
    db.commit()
    return RedirectResponse(url="/positions", status_code=303)

@router.get("/{position_id}", response_class=HTMLResponse)
async def read_position(request: Request, position_id: int, db: Session = Depends(get_db)):
    position = db.query(Position).filter(Position.position_id == position_id).first()
    if position is None:
        raise HTTPException(status_code=404, detail="Position not found")
    return templates.TemplateResponse(
        "positions/detail.html",
        {"request": request, "position": position}
    )

@router.get("/{position_id}/edit", response_class=HTMLResponse)
async def edit_position_form(request: Request, position_id: int, db: Session = Depends(get_db)):
    position = db.query(Position).filter(Position.position_id == position_id).first()
    if position is None:
        raise HTTPException(status_code=404, detail="Position not found")
    return templates.TemplateResponse(
        "positions/edit.html",
        {"request": request, "position": position}
    )

@router.post("/{position_id}/edit")
async def edit_position(
    request: Request,
    position_id: int,
    title: str = Form(...),
    base_salary_full: float = Form(...),
    base_salary_part: float = Form(...),
    allowances: float = Form(...),
    description: str = Form(...),
    required_skills: str = Form(...),
    db: Session = Depends(get_db)
):
    position = db.query(Position).filter(Position.position_id == position_id).first()
    if position is None:
        raise HTTPException(status_code=404, detail="Position not found")
    
    position.title = title
    position.base_salary_full = base_salary_full
    position.base_salary_part = base_salary_part
    position.allowances = allowances
    position.description = description
    position.required_skills = required_skills
    
    db.commit()
    return RedirectResponse(url=f"/positions/{position_id}", status_code=303)

@router.post("/{position_id}/delete")
async def delete_position(position_id: int, db: Session = Depends(get_db)):
    position = db.query(Position).filter(Position.position_id == position_id).first()
    if position is None:
        raise HTTPException(status_code=404, detail="Position not found")
    db.delete(position)
    db.commit()
    return RedirectResponse(url="/positions", status_code=303)