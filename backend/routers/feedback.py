from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from backend.database import get_db
from backend.models.models import MessFeedback, Student
from backend.schemas.schemas import MessFeedbackCreate, MessFeedbackResponse

router = APIRouter(prefix="/feedback", tags=["Mess Feedback"])

@router.get("", response_model=List[MessFeedbackResponse])
def get_feedback(db: Session = Depends(get_db)):
    feedbacks = db.query(MessFeedback).order_by(MessFeedback.created_at.desc()).all()
    results = []
    for f in feedbacks:
        student = db.query(Student).filter(Student.id == f.student_id).first()
        results.append(
            MessFeedbackResponse(
                id=f.id,
                student_id=f.student_id,
                student_name=student.user.full_name if (student and student.user) else "Student",
                meal_type=f.meal_type,
                rating=f.rating,
                hygiene_rating=f.hygiene_rating,
                taste_rating=f.taste_rating,
                comments=f.comments,
                date=f.date,
                created_at=f.created_at,
            )
        )
    return results

@router.post("", response_model=MessFeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_feedback(data: MessFeedbackCreate, db: Session = Depends(get_db)):
    student = db.query(Student).filter((Student.id == data.student_id) | (Student.user_id == data.student_id)).first()
    student_id = student.id if student else data.student_id

    new_fb = MessFeedback(
        student_id=student_id,
        meal_type=data.meal_type,
        rating=data.rating,
        hygiene_rating=data.hygiene_rating,
        taste_rating=data.taste_rating,
        comments=data.comments,
        date=data.date or datetime.utcnow().strftime("%Y-%m-%d"),
    )
    db.add(new_fb)
    db.commit()
    db.refresh(new_fb)

    return MessFeedbackResponse(
        id=new_fb.id,
        student_id=new_fb.student_id,
        student_name=student.user.full_name if (student and student.user) else "Student",
        meal_type=new_fb.meal_type,
        rating=new_fb.rating,
        hygiene_rating=new_fb.hygiene_rating,
        taste_rating=new_fb.taste_rating,
        comments=new_fb.comments,
        date=new_fb.date,
        created_at=new_fb.created_at,
    )
