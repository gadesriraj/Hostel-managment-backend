from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.models.models import Room, Student
from backend.schemas.schemas import RoomResponse, RoomCreate, RoomUpdate

router = APIRouter(prefix="/rooms", tags=["Rooms"])

@router.get("", response_model=List[RoomResponse])
def get_rooms(
    block: Optional[str] = None,
    floor: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Room)
    if block:
        query = query.filter(Room.block == block)
    if floor is not None:
        query = query.filter(Room.floor == floor)
    if status:
        query = query.filter(Room.status == status)

    rooms = query.all()
    results = []
    for r in rooms:
        residents = db.query(Student).filter(Student.room_id == r.id).all()
        occupants_data = [
            {
                "id": s.id,
                "full_name": s.user.full_name if s.user else "Student",
                "enrollment_no": s.enrollment_no,
                "department": s.department,
            }
            for s in residents
        ]
        results.append(
            RoomResponse(
                id=r.id,
                room_number=r.room_number,
                hostel_name=r.hostel_name,
                block=r.block,
                floor=r.floor,
                capacity=r.capacity,
                type=r.type,
                status=r.status,
                amenities=r.amenities or [],
                current_occupants=len(residents),
                occupants=occupants_data,
            )
        )
    return results

@router.post("", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(data: RoomCreate, db: Session = Depends(get_db)):
    existing = db.query(Room).filter(Room.room_number == data.room_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Room number already exists")

    new_room = Room(
        room_number=data.room_number,
        hostel_name=data.hostel_name,
        block=data.block,
        floor=data.floor,
        capacity=data.capacity,
        type=data.type,
        status="available",
        amenities=data.amenities,
    )
    db.add(new_room)
    db.commit()
    db.refresh(new_room)

    return RoomResponse(
        id=new_room.id,
        room_number=new_room.room_number,
        hostel_name=new_room.hostel_name,
        block=new_room.block,
        floor=new_room.floor,
        capacity=new_room.capacity,
        type=new_room.type,
        status=new_room.status,
        amenities=new_room.amenities or [],
        current_occupants=0,
        occupants=[],
    )

@router.put("/{id}", response_model=RoomResponse)
def update_room(id: str, data: RoomUpdate, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(room, key, value)

    # Check capacity vs occupants
    residents = db.query(Student).filter(Student.room_id == room.id).all()
    count = len(residents)
    if count == 0 and room.status != "maintenance":
        room.status = "available"
    elif count >= room.capacity:
        room.status = "full"
    elif count > 0:
        room.status = "partially_occupied"

    db.commit()
    db.refresh(room)

    return RoomResponse(
        id=room.id,
        room_number=room.room_number,
        hostel_name=room.hostel_name,
        block=room.block,
        floor=room.floor,
        capacity=room.capacity,
        type=room.type,
        status=room.status,
        amenities=room.amenities or [],
        current_occupants=count,
        occupants=[{"id": s.id, "full_name": s.user.full_name if s.user else "Student"} for s in residents],
    )

@router.delete("/{id}")
def delete_room(id: str, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # Unassign students
    db.query(Student).filter(Student.room_id == id).update({"room_id": None})
    db.delete(room)
    db.commit()
    return {"message": "Room deleted successfully"}
