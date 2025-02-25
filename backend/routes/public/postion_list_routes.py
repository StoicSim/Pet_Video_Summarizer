from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from models import Position
from base import SessionLocal

router = APIRouter(
    prefix="/position_list",
    tags=["position_list"]
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
        "public/position_list.html",
        {"request": request, "positions": positions}
    )