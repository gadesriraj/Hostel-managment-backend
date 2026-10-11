from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.models.models import Visitor, Student, Room, Notification
from backend.schemas.schemas import VisitorCreate, VisitorUpdate, VisitorResponse

router = APIRouter(prefix="/visitors", tags=["Visitors"])

@router.get("", response_model=List[VisitorResponse])
def get_visitors(
    student_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Visitor)
    if student_id:
        query = query.filter(Visitor.student_id == student_id)
    if status:
        query = query.filter(Visitor.status == status)

    visitors = query.order_by(Visitor.created_at.desc()).all()
    results = []
    for v in visitors:
        student = db.query(Student).filter(Student.id == v.student_id).first()
        room = db.query(Room).filter(Room.id == student.room_id).first() if (student and student.room_id) else None

        results.append(
            VisitorResponse(
                id=v.id,
                student_id=v.student_id,
                student_name=student.user.full_name if (student and student.user) else "Student",
                room_number=room.room_number if room else "N/A",
                visitor_name=v.visitor_name,
                phone_number=v.phone_number,
                relationship=v.relationship,
                visit_date=v.visit_date,
                entry_time=v.entry_time,
                expected_exit_time=v.expected_exit_time,
                actual_exit_time=v.actual_exit_time,
                purpose=v.purpose,
                status=v.status,
                approved_by=v.approved_by,
                rejection_reason=v.rejection_reason,
                created_at=v.created_at,
            )
        )
    return results

@router.post("", response_model=VisitorResponse, status_code=status.HTTP_201_CREATED)
def register_visitor(data: VisitorCreate, db: Session = Depends(get_db)):
    student = db.query(Student).filter((Student.id == data.student_id) | (Student.user_id == data.student_id)).first()
    if not student:
        raise HTTPException(status_code=400, detail="Student not found")

    new_v = Visitor(
        student_id=student.id,
        visitor_name=data.visitor_name,
        phone_number=data.phone_number,
        relationship=data.relationship,
        visit_date=data.visit_date,
        entry_time=data.entry_time,
        expected_exit_time=data.expected_exit_time,
        purpose=data.purpose,
        status="pending",
    )
    db.add(new_v)
    db.commit()
    db.refresh(new_v)

    room = db.query(Room).filter(Room.id == student.room_id).first() if student.room_id else None

    return VisitorResponse(
        id=new_v.id,
        student_id=new_v.student_id,
        student_name=student.user.full_name if student.user else "Student",
        room_number=room.room_number if room else "N/A",
        visitor_name=new_v.visitor_name,
        phone_number=new_v.phone_number,
        relationship=new_v.relationship,
        visit_date=new_v.visit_date,
        entry_time=new_v.entry_time,
        expected_exit_time=new_v.expected_exit_time,
        actual_exit_time=None,
        purpose=new_v.purpose,
        status=new_v.status,
        approved_by=None,
        rejection_reason=None,
        created_at=new_v.created_at,
    )

@router.put("/{id}", response_model=VisitorResponse)
def update_visitor_status(id: str, data: VisitorUpdate, db: Session = Depends(get_db)):
    v = db.query(Visitor).filter(Visitor.id == id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Visitor entry not found")

    if data.status:
        v.status = data.status
    if data.rejection_reason is not None:
        v.rejection_reason = data.rejection_reason
    if data.approved_by:
        v.approved_by = data.approved_by
    if data.actual_exit_time:
        v.actual_exit_time = data.actual_exit_time

    db.commit()
    db.refresh(v)

    student = db.query(Student).filter(Student.id == v.student_id).first()
    room = db.query(Room).filter(Room.id == student.room_id).first() if (student and student.room_id) else None

    return VisitorResponse(
        id=v.id,
        student_id=v.student_id,
        student_name=student.user.full_name if (student and student.user) else "Student",
        room_number=room.room_number if room else "N/A",
        visitor_name=v.visitor_name,
        phone_number=v.phone_number,
        relationship=v.relationship,
        visit_date=v.visit_date,
        entry_time=v.entry_time,
        expected_exit_time=v.expected_exit_time,
        actual_exit_time=v.actual_exit_time,
        purpose=v.purpose,
        status=v.status,
        approved_by=v.approved_by,
        rejection_reason=v.rejection_reason,
        created_at=v.created_at,
    )
