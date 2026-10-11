from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from backend.database import get_db
from backend.models.models import RoomAllocation, Student, Room, Notification
from backend.schemas.schemas import AllocationCreate, AllocationResponse

router = APIRouter(prefix="/allocations", tags=["Room Allocation"])

@router.post("", response_model=AllocationResponse, status_code=status.HTTP_201_CREATED)
def allocate_room(data: AllocationCreate, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == data.student_id).first()
    room = db.query(Room).filter(Room.id == data.room_id).first()

    if not student or not room:
        raise HTTPException(status_code=400, detail="Invalid student or room ID")

    # Check capacity
    current_occupants = db.query(Student).filter(Student.room_id == room.id).count()
    if current_occupants >= room.capacity:
        raise HTTPException(status_code=400, detail="Selected room is already at full capacity")

    student.room_id = room.id

    new_allocation = RoomAllocation(
        student_id=student.id,
        room_id=room.id,
        allocated_by=data.allocated_by or "admin",
        allocation_date=datetime.utcnow(),
        status="active",
        notes=data.notes,
    )
    db.add(new_allocation)

    # Notify student
    notif = Notification(
        user_id=student.user_id,
        title="Room Allocated",
        message=f"You have been allocated Room {room.room_number} in {room.block}.",
        type="room_allocation",
    )
    db.add(notif)

    db.commit()
    db.refresh(new_allocation)
    return new_allocation

@router.delete("/{student_id}")
def deallocate_room(student_id: str, db: Session = Depends(get_db)):
    student = db.query(Student).filter((Student.id == student_id) | (Student.user_id == student_id)).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    student.room_id = None
    db.query(RoomAllocation).filter(
        RoomAllocation.student_id == student.id,
        RoomAllocation.status == "active"
    ).update({"status": "vacated", "vacated_date": datetime.utcnow()})

    notif = Notification(
        user_id=student.user_id,
        title="Room Allocation Vacated",
        message="Your hostel room allocation has been released.",
        type="room_allocation",
    )
    db.add(notif)

    db.commit()
    return {"message": "Room deallocated successfully"}
