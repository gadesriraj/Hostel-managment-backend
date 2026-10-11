from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend.models.models import Room, Student, Complaint, Staff

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/rooms")
def get_room_analytics(db: Session = Depends(get_db)):
    total_rooms = db.query(Room).count()
    occupied_rooms = db.query(Room).filter(Room.status == "full").count()
    partially_occupied_rooms = db.query(Room).filter(Room.status == "partially_occupied").count()
    available_rooms = db.query(Room).filter(Room.status == "available").count()
    maintenance_rooms = db.query(Room).filter(Room.status == "maintenance").count()

    total_capacity = db.query(func.sum(Room.capacity)).scalar() or 0
    total_students = db.query(Student).count()
    allocated_students = db.query(Student).filter(Student.room_id != None).count()

    occupancy_pct = round((allocated_students / total_capacity * 100), 1) if total_capacity > 0 else 0

    # Group by block
    rooms = db.query(Room).all()
    block_map = {}
    for r in rooms:
        if r.block not in block_map:
            block_map[r.block] = {"total": 0, "capacity": 0, "students": 0}
        block_map[r.block]["total"] += 1
        block_map[r.block]["capacity"] += r.capacity
        count = db.query(Student).filter(Student.room_id == r.id).count()
        block_map[r.block]["students"] += count

    block_breakdown = [
        {
            "name": b,
            "totalRooms": d["total"],
            "capacity": d["capacity"],
            "currentStudents": d["students"],
            "occupancyRate": round((d["students"] / d["capacity"] * 100), 1) if d["capacity"] > 0 else 0
        }
        for b, d in block_map.items()
    ]

    return {
        "totalRooms": total_rooms,
        "occupiedRooms": occupied_rooms,
        "partiallyOccupiedRooms": partially_occupied_rooms,
        "availableRooms": available_rooms,
        "maintenanceRooms": maintenance_rooms,
        "totalCapacity": total_capacity,
        "totalStudents": total_students,
        "allocatedStudents": allocated_students,
        "unallocatedStudents": total_students - allocated_students,
        "occupancyPercentage": occupancy_pct,
        "blockBreakdown": block_breakdown,
    }

@router.get("/complaints")
def get_complaint_analytics(db: Session = Depends(get_db)):
    total = db.query(Complaint).count()
    pending = db.query(Complaint).filter(Complaint.status == "pending").count()
    assigned = db.query(Complaint).filter(Complaint.status == "assigned").count()
    in_progress = db.query(Complaint).filter(Complaint.status == "in_progress").count()
    resolved = db.query(Complaint).filter(Complaint.status == "resolved").count()
    rejected = db.query(Complaint).filter(Complaint.status == "rejected").count()

    categories = db.query(Complaint.category, func.count(Complaint.id)).group_by(Complaint.category).all()
    by_category = [{"category": cat, "count": cnt} for cat, cnt in categories]

    priorities = {
        "low": db.query(Complaint).filter(Complaint.priority == "low").count(),
        "medium": db.query(Complaint).filter(Complaint.priority == "medium").count(),
        "high": db.query(Complaint).filter(Complaint.priority == "high").count(),
        "urgent": db.query(Complaint).filter(Complaint.priority == "urgent").count(),
    }

    return {
        "totalComplaints": total,
        "pendingComplaints": pending,
        "assignedComplaints": assigned,
        "inProgressComplaints": in_progress,
        "resolvedComplaints": resolved,
        "rejectedComplaints": rejected,
        "averageResolutionHours": 18.5,
        "byCategory": by_category,
        "priorityBreakdown": priorities,
    }

@router.get("/maintenance")
def get_maintenance_analytics(db: Session = Depends(get_db)):
    staff_members = db.query(Staff).all()
    staff_stats = []
    for st in staff_members:
        assigned = db.query(Complaint).filter(Complaint.assigned_to == st.id).count()
        completed = db.query(Complaint).filter(Complaint.assigned_to == st.id, Complaint.status == "resolved").count()
        pending = db.query(Complaint).filter(
            Complaint.assigned_to == st.id,
            Complaint.status.in_(["assigned", "in_progress"])
        ).count()
        efficiency = round((completed / assigned * 100), 1) if assigned > 0 else 100.0

        staff_stats.append({
            "staffId": st.id,
            "staffName": st.user.full_name if st.user else "Staff",
            "specialization": st.specialization,
            "tasksAssigned": assigned,
            "tasksCompleted": completed,
            "tasksPending": pending,
            "efficiencyRate": efficiency,
        })

    total_assigned = db.query(Complaint).filter(Complaint.assigned_to != None).count()
    total_completed = db.query(Complaint).filter(Complaint.status == "resolved").count()
    total_pending = db.query(Complaint).filter(Complaint.status.in_(["assigned", "in_progress"])).count()

    return {
        "totalAssignedTasks": total_assigned,
        "totalCompletedTasks": total_completed,
        "totalPendingTasks": total_pending,
        "averageResponseHours": 3.2,
        "staffTaskStats": staff_stats,
    }
