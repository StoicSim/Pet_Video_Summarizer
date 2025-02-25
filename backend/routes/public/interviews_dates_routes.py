from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session,joinedload
from datetime import date
from datetime import date, time

from models import Interview,User,Applicant
from base import SessionLocal

router = APIRouter(
    prefix="/interview_dates",
    tags=["interview_dates"]
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
async def list_interviews(request: Request, db: Session = Depends(get_db)):
    # Query interviews with explicit joins
    interviews = (
        db.query(Interview)
        .options(
            joinedload(Interview.applicant),
            joinedload(Interview.interviewer)
        )
        .join(User, Interview.interviewed_by == User.user_id, isouter=True)
        .join(Applicant, Interview.applicant_id == Applicant.applicant_id, isouter=True)
        .order_by(Interview.interview_date.desc(), Interview.interview_time.desc())
        .all()
    )
      
    formatted_interviews = []
    for interview in interviews:
        
        
        formatted_interviews.append({
            'interview_id': interview.interview_id,
            'applicant': {
                'name': interview.applicant.full_name if interview.applicant else 'N/A',
                'id': interview.applicant_id
            },
            'interview_date': interview.interview_date.strftime('%Y-%m-%d') if interview.interview_date else 'N/A',
            'interview_time': interview.interview_time.strftime('%H:%M') if interview.interview_time else 'N/A',
            'interview_status': interview.interview_status,
            'interviewer': {
                'name': interview.interviewer.username if interview.interviewer else 'Not Assigned',
                'id': interview.interviewed_by
            },
            'interview_notes': interview.interview_notes or ''
        })

    return templates.TemplateResponse(
        "public/interview_dates.html",
        {
            "request": request, 
            "interviews": formatted_interviews
        }
    )