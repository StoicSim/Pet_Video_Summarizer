# routes/private/dashboard_routes.py
from fastapi import APIRouter, Request, Depends,status
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.templating import Jinja2Templates
from auth import get_current_user
from models import User
from sqlalchemy.orm import Session
from auth import get_db

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request,
            "user": current_user
        }
    )