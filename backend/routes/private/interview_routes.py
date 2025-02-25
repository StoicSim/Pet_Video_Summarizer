
from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session,joinedload
from datetime import date
from datetime import time,datetime
 

from enums import InterviewStatus


from models import Interview,User,Applicant
from enums import LeaveStatus, EmploymentStatus
from base import SessionLocal

router = APIRouter(
    prefix="/interviews",
    tags=["interviews"]
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
    
    # Add some debug logging
    print(f"Found {len(interviews)} interviews")
    
    formatted_interviews = []
    for interview in interviews:
        # Debug print
        print(f"Interview ID: {interview.interview_id}")
        print(f"Applicant ID: {interview.applicant_id}")
        print(f"Interviewer ID: {interview.interviewed_by}")
        print(f"Applicant: {interview.applicant}")
        print(f"Interviewer: {interview.interviewer}")
        
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
        "interviews/list.html",
        {
            "request": request, 
            "interviews": formatted_interviews
        }
    )

@router.get("/create", response_class=HTMLResponse)
async def create_interview_form(request: Request, db: Session = Depends(get_db)):
    # Get all applicants
    applicants = db.query(Applicant).all()
    
    # Get all users who can be interviewers
    users = db.query(User).all()
    
    return templates.TemplateResponse(
        "interviews/create.html",
        {
            "request": request,
            "applicants": applicants,
            "users": users,
            "interview_statuses": InterviewStatus
        }
    )

@router.post("/create")
async def create_interview(
    request: Request,
    applicant_id: int = Form(...),
    interview_date: str = Form(...),
    interview_time: str = Form(...),
    interview_status: InterviewStatus = Form(...),
    interviewed_by: int = Form(...),
    interview_notes: str = Form(None),
    db: Session = Depends(get_db)
):
    try:
        # Convert string dates and times to proper Python objects
        parsed_date = datetime.strptime(interview_date, '%Y-%m-%d').date()
        parsed_time = datetime.strptime(interview_time, '%H:%M').time()
        
        # Create new interview
        interview = Interview(
            applicant_id=applicant_id,
            interview_date=parsed_date,
            interview_time=parsed_time,
            interview_status=interview_status,
            interviewed_by=interviewed_by,
            interview_notes=interview_notes if interview_notes else None
        )
        
        db.add(interview)
        db.commit()
        
        return RedirectResponse(url="/interviews", status_code=303)
        
    except Exception as e:
        db.rollback()
        print(f"Error creating interview: {str(e)}")
        return templates.TemplateResponse(
            "interviews/create.html",
            {
                "request": request,
                "error": "Failed to create interview. Please try again.",
                "applicants": db.query(Applicant).all(),
                "users": db.query(User).all(),
                "interview_statuses": InterviewStatus
            },
            status_code=400
        )

@router.post("/{interview_id}/delete")
async def delete_position(interview_id: int, db: Session = Depends(get_db)):
    id = db.query(Interview).filter(Interview.interview_id == interview_id).first()
    if id is None:
        raise HTTPException(status_code=404, detail="Position not found")
    db.delete(id)
    db.commit()
    return RedirectResponse(url="/interviews", status_code=303)


@router.get("/{interview_id}/edit", response_class=HTMLResponse)
async def edit_interview_form(request: Request, interview_id: int, db: Session = Depends(get_db)):
    interview = db.query(Interview).filter(Interview.interview_id == interview_id).first()
    if interview is None:
        raise HTTPException(status_code=404, detail="Interview not found")
    return templates.TemplateResponse(
        "interviews/edit.html",
        {"request": request, "interview": interview}
    )
@router.get("/{interview_id}", response_class=HTMLResponse)
async def view_interview(request: Request, interview_id: int, db: Session = Depends(get_db)):
    interview = (
        db.query(Interview)
        .options(
            joinedload(Interview.applicant),
            joinedload(Interview.interviewer)
        )
        .filter(Interview.interview_id == interview_id)
        .first()
    )
    if interview is None:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    return templates.TemplateResponse(
        "interviews/view.html",
        {"request": request, "interview": interview}
    )

@router.post("/{interview_id}/edit")
async def edit_interview(
    request: Request,
    interview_id: int,
    applicant_id: int = Form(...),
    interview_date: date = Form(...),
    interview_time: time = Form(...),
    interview_status: InterviewStatus = Form(...),
    interviewed_by: int = Form(...),
    interview_notes: str = Form(...),
    db: Session = Depends(get_db)
):
    interview = db.query(Interview).filter(Interview.interview_id == interview_id).first()
    if interview is None:
        raise HTTPException(status_code=404, detail="Interview not found")
        
    interview.applicant_id = applicant_id
    interview.interview_date = interview_date
    interview.interview_time = interview_time
    interview.interview_status = interview_status
    interview.interviewed_by = interviewed_by
    interview.interview_notes = interview_notes
    
    db.commit()
    return RedirectResponse(url=f"/interviews/{interview_id}", status_code=303)