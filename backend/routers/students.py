from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models.models import Student, Room, User
from backend.schemas.schemas import StudentResponse, StudentUpdate

router = APIRouter(prefix="/students", tags=["Students"])

@router.get("", response_model=List[StudentResponse])
def get_students(db: Session = Depends(get_db)):
    students = db.query(Student).all()
    results = []
    for s in students:
        room = db.query(Room).filter(Room.id == s.room_id).first() if s.room_id else None
        results.append(
            StudentResponse(
                id=s.id,
                user_id=s.user_id,
                full_name=s.user.full_name if s.user else "Student",
                email=s.user.email if s.user else "",
                enrollment_no=s.enrollment_no,
                department=s.department,
                year_of_study=s.year_of_study,
                gender=s.gender,
                emergency_contact=s.emergency_contact,
                blood_group=s.blood_group,
                room_id=s.room_id,
                room_number=room.room_number if room else None,
                block=room.block if room else None,
                floor=room.floor if room else None,
                hostel_name=s.hostel_name,
                created_at=s.created_at,
            )
        )
    return results

@router.get("/{id}")
def get_student_by_id(id: str, db: Session = Depends(get_db)):
    student = db.query(Student).filter((Student.id == id) | (Student.user_id == id)).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    room = db.query(Room).filter(Room.id == student.room_id).first() if student.room_id else None
    roommates = []
    if student.room_id:
        rms = db.query(Student).filter(Student.room_id == student.room_id, Student.id != student.id).all()
        for rm in rms:
            roommates.append({
                "id": rm.id,
                "full_name": rm.user.full_name if rm.user else "Roommate",
                "email": rm.user.email if rm.user else "",
                "enrollment_no": rm.enrollment_no,
                "department": rm.department,
                "year_of_study": rm.year_of_study
            })

    return {
        "id": student.id,
        "user_id": student.user_id,
        "full_name": student.user.full_name if student.user else "",
        "email": student.user.email if student.user else "",
        "enrollment_no": student.enrollment_no,
        "department": student.department,
        "year_of_study": student.year_of_study,
        "gender": student.gender,
        "emergency_contact": student.emergency_contact,
        "blood_group": student.blood_group,
        "hostel_name": student.hostel_name,
        "room_id": student.room_id,
        "room": {
            "id": room.id,
            "room_number": room.room_number,
            "block": room.block,
            "floor": room.floor,
            "capacity": room.capacity,
            "type": room.type,
            "status": room.status,
            "amenities": room.amenities,
        } if room else None,
        "roommates": roommates,
    }

@router.put("/{id}")
def update_student(id: str, data: StudentUpdate, db: Session = Depends(get_db)):
    student = db.query(Student).filter((Student.id == id) | (Student.user_id == id)).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if data.department is not None:
        student.department = data.department
    if data.year_of_study is not None:
        student.year_of_study = data.year_of_study
    if data.emergency_contact is not None:
        student.emergency_contact = data.emergency_contact
    if data.blood_group is not None:
        student.blood_group = data.blood_group

    user = student.user
    if user:
        if data.full_name is not None:
            user.full_name = data.full_name
        if data.phone is not None:
            user.phone = data.phone

    db.commit()
    db.refresh(student)
    return {"message": "Student updated successfully", "student": student}
