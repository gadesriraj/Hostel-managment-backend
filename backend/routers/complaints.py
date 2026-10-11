from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from backend.database import get_db
from backend.models.models import Complaint, Student, Room, Staff, Notification
from backend.schemas.schemas import ComplaintResponse, ComplaintCreate, ComplaintUpdate

router = APIRouter(prefix="/complaints", tags=["Complaints"])

@router.get("", response_model=List[ComplaintResponse])
def get_complaints(
    student_id: Optional[str] = None,
    staff_id: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Complaint)
    if student_id:
        query = query.filter(Complaint.student_id == student_id)
    if staff_id:
        query = query.filter(Complaint.assigned_to == staff_id)
    if status:
        query = query.filter(Complaint.status == status)
    if category:
        query = query.filter(Complaint.category.ilike(category))
    if priority:
        query = query.filter(Complaint.priority == priority)

    complaints = query.order_by(Complaint.created_at.desc()).all()
    results = []
    for c in complaints:
        student = db.query(Student).filter(Student.id == c.student_id).first()
        room = db.query(Room).filter(Room.id == c.room_id).first() if c.room_id else None
        staff = db.query(Staff).filter(Staff.id == c.assigned_to).first() if c.assigned_to else None

        results.append(
            ComplaintResponse(
                id=c.id,
                complaint_code=c.complaint_code,
                student_id=c.student_id,
                student_name=student.user.full_name if (student and student.user) else "Student",
                room_id=c.room_id,
                room_number=room.room_number if room else "N/A",
                category=c.category,
                title=c.title,
                description=c.description,
                priority=c.priority,
                status=c.status,
                assigned_to=c.assigned_to,
                assigned_to_name=staff.user.full_name if (staff and staff.user) else None,
                assigned_at=c.assigned_at,
                resolved_at=c.resolved_at,
                resolution_notes=c.resolution_notes,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
        )
    return results

@router.post("", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
def create_complaint(data: ComplaintCreate, db: Session = Depends(get_db)):
    student = db.query(Student).filter((Student.id == data.student_id) | (Student.user_id == data.student_id)).first()
    if not student:
        raise HTTPException(status_code=400, detail="Student not found")

    count = db.query(Complaint).count() + 1
    complaint_code = f"CMP-2026-{str(count).zfill(3)}"

    new_c = Complaint(
        complaint_code=complaint_code,
        student_id=student.id,
        room_id=student.room_id,
        category=data.category,
        title=data.title,
        description=data.description,
        priority=data.priority,
        status="pending",
    )
    db.add(new_c)
    db.commit()
    db.refresh(new_c)

    room = db.query(Room).filter(Room.id == student.room_id).first() if student.room_id else None

    return ComplaintResponse(
        id=new_c.id,
        complaint_code=new_c.complaint_code,
        student_id=student.id,
        student_name=student.user.full_name if student.user else "Student",
        room_id=student.room_id,
        room_number=room.room_number if room else "N/A",
        category=new_c.category,
        title=new_c.title,
        description=new_c.description,
        priority=new_c.priority,
        status=new_c.status,
        assigned_to=None,
        assigned_to_name=None,
        assigned_at=None,
        resolved_at=None,
        resolution_notes=None,
        created_at=new_c.created_at,
        updated_at=new_c.updated_at,
    )

@router.get("/{id}", response_model=ComplaintResponse)
def get_complaint(id: str, db: Session = Depends(get_db)):
    c = db.query(Complaint).filter(Complaint.id == id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Complaint not found")

    student = db.query(Student).filter(Student.id == c.student_id).first()
    room = db.query(Room).filter(Room.id == c.room_id).first() if c.room_id else None
    staff = db.query(Staff).filter(Staff.id == c.assigned_to).first() if c.assigned_to else None

    return ComplaintResponse(
        id=c.id,
        complaint_code=c.complaint_code,
        student_id=c.student_id,
        student_name=student.user.full_name if (student and student.user) else "Student",
        room_id=c.room_id,
        room_number=room.room_number if room else "N/A",
        category=c.category,
        title=c.title,
        description=c.description,
        priority=c.priority,
        status=c.status,
        assigned_to=c.assigned_to,
        assigned_to_name=staff.user.full_name if (staff and staff.user) else None,
        assigned_at=c.assigned_at,
        resolved_at=c.resolved_at,
        resolution_notes=c.resolution_notes,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )

@router.put("/{id}", response_model=ComplaintResponse)
def update_complaint(id: str, data: ComplaintUpdate, db: Session = Depends(get_db)):
    c = db.query(Complaint).filter(Complaint.id == id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Complaint not found")

    if data.priority:
        c.priority = data.priority

    if data.assigned_to is not None:
        if data.assigned_to == "":
            c.assigned_to = None
            c.assigned_at = None
            if c.status == "assigned":
                c.status = "pending"
        else:
            staff = db.query(Staff).filter((Staff.id == data.assigned_to) | (Staff.user_id == data.assigned_to)).first()
            if staff:
                c.assigned_to = staff.id
                c.assigned_at = datetime.utcnow()
                if c.status == "pending":
                    c.status = "assigned"

    if data.status:
        c.status = data.status
        if data.status == "resolved":
            c.resolved_at = datetime.utcnow()

    if data.resolution_notes is not None:
        c.resolution_notes = data.resolution_notes

    c.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(c)

    student = db.query(Student).filter(Student.id == c.student_id).first()
    room = db.query(Room).filter(Room.id == c.room_id).first() if c.room_id else None
    staff = db.query(Staff).filter(Staff.id == c.assigned_to).first() if c.assigned_to else None

    return ComplaintResponse(
        id=c.id,
        complaint_code=c.complaint_code,
        student_id=c.student_id,
        student_name=student.user.full_name if (student and student.user) else "Student",
        room_id=c.room_id,
        room_number=room.room_number if room else "N/A",
        category=c.category,
        title=c.title,
        description=c.description,
        priority=c.priority,
        status=c.status,
        assigned_to=c.assigned_to,
        assigned_to_name=staff.user.full_name if (staff and staff.user) else None,
        assigned_at=c.assigned_at,
        resolved_at=c.resolved_at,
        resolution_notes=c.resolution_notes,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )
