from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from backend.models.models import (
    User,
    Student,
    Staff,
    Room,
    RoomAllocation,
    Complaint,
    Visitor,
    Notice,
    MessFeedback,
    Notification,
)
from backend.services.auth_service import get_password_hash

def seed_database(db: Session):
    if db.query(User).count() > 0:
        return

    print("Seeding database with demo data...")

    # Users
    warden_user = User(
        id="usr-warden-1",
        email="warden@hostelsync.edu",
        password_hash=get_password_hash("admin123"),
        full_name="Dr. Robert Vance",
        role="warden",
        phone="+1 (555) 234-5678",
    )
    db.add(warden_user)

    s1_user = User(
        id="usr-student-1",
        email="student@hostelsync.edu",
        password_hash=get_password_hash("student123"),
        full_name="Alex Morgan",
        role="student",
        phone="+1 (555) 345-6789",
    )
    s2_user = User(
        id="usr-student-2",
        email="priya@hostelsync.edu",
        password_hash=get_password_hash("student123"),
        full_name="Priya Sharma",
        role="student",
        phone="+1 (555) 456-7890",
    )
    s3_user = User(
        id="usr-student-3",
        email="marcus@hostelsync.edu",
        password_hash=get_password_hash("student123"),
        full_name="Marcus Chen",
        role="student",
        phone="+1 (555) 567-8901",
    )
    db.add_all([s1_user, s2_user, s3_user])

    st1_user = User(
        id="usr-staff-1",
        email="staff@hostelsync.edu",
        password_hash=get_password_hash("staff123"),
        full_name="David Miller",
        role="staff",
        phone="+1 (555) 890-1234",
    )
    st2_user = User(
        id="usr-staff-2",
        email="carlos@hostelsync.edu",
        password_hash=get_password_hash("staff123"),
        full_name="Carlos Mendez",
        role="staff",
        phone="+1 (555) 901-2345",
    )
    db.add_all([st1_user, st2_user])
    db.flush()

    # Rooms
    r1 = Room(
        id="rm-101",
        room_number="A-101",
        hostel_name="Horizon Hall",
        block="Block A",
        floor=1,
        capacity=2,
        type="Standard Double (Non-AC)",
        status="available",
        amenities=["High-speed Wi-Fi", "Study Tables", "Attached Balcony"],
    )
    r2 = Room(
        id="rm-204",
        room_number="A-204",
        hostel_name="Horizon Hall",
        block="Block A",
        floor=2,
        capacity=2,
        type="Deluxe Double (AC)",
        status="full",
        amenities=["Air Conditioning", "High-speed Wi-Fi", "Attached Bathroom"],
    )
    r3 = Room(
        id="rm-302",
        room_number="B-102",
        hostel_name="Pinnacle Tower",
        block="Block B",
        floor=1,
        capacity=2,
        type="Standard Double (Non-AC)",
        status="partially_occupied",
        amenities=["High-speed Wi-Fi", "Study Tables", "Garden View"],
    )
    db.add_all([r1, r2, r3])
    db.flush()

    # Students
    std1 = Student(
        id="std-1",
        user_id=s1_user.id,
        enrollment_no="CS-2023-042",
        department="Computer Science & Engineering",
        year_of_study=3,
        gender="Male",
        emergency_contact="+1 (555) 987-6543 (Parent)",
        blood_group="O+",
        room_id=r2.id,
    )
    std2 = Student(
        id="std-2",
        user_id=s2_user.id,
        enrollment_no="EE-2024-118",
        department="Electrical Engineering",
        year_of_study=2,
        gender="Female",
        emergency_contact="+1 (555) 876-5432 (Guardian)",
        blood_group="B+",
        room_id=r3.id,
    )
    std3 = Student(
        id="std-3",
        user_id=s3_user.id,
        enrollment_no="ME-2023-089",
        department="Mechanical Engineering",
        year_of_study=3,
        gender="Male",
        emergency_contact="+1 (555) 765-4321 (Parent)",
        blood_group="A+",
        room_id=r2.id, # Roommate of std1
    )
    db.add_all([std1, std2, std3])
    db.flush()

    # Staff
    staff1 = Staff(
        id="stf-1",
        user_id=st1_user.id,
        employee_id="EMP-ELEC-04",
        specialization="Electrical & AC Maintenance",
        phone="+1 (555) 890-1234",
        status="available",
    )
    staff2 = Staff(
        id="stf-2",
        user_id=st2_user.id,
        employee_id="EMP-PLUM-02",
        specialization="Plumbing & Drainage",
        phone="+1 (555) 901-2345",
        status="busy",
    )
    db.add_all([staff1, staff2])
    db.flush()

    # Allocations
    al1 = RoomAllocation(
        student_id=std1.id,
        room_id=r2.id,
        allocated_by=warden_user.id,
        allocation_date=datetime.utcnow() - timedelta(days=60),
        status="active",
    )
    al2 = RoomAllocation(
        student_id=std3.id,
        room_id=r2.id,
        allocated_by=warden_user.id,
        allocation_date=datetime.utcnow() - timedelta(days=60),
        status="active",
    )
    al3 = RoomAllocation(
        student_id=std2.id,
        room_id=r3.id,
        allocated_by=warden_user.id,
        allocation_date=datetime.utcnow() - timedelta(days=45),
        status="active",
    )
    db.add_all([al1, al2, al3])

    # Complaints
    c1 = Complaint(
        id="cmp-1",
        complaint_code="CMP-2026-001",
        student_id=std1.id,
        room_id=r2.id,
        category="Electrical",
        title="Ceiling fan making clicking noise on high speeds",
        description="Regulator vibrates heavily and clicking noise occurs on speeds 4 and 5.",
        priority="medium",
        status="assigned",
        assigned_to=staff1.id,
        assigned_at=datetime.utcnow() - timedelta(hours=12),
    )
    c2 = Complaint(
        id="cmp-2",
        complaint_code="CMP-2026-002",
        student_id=std2.id,
        room_id=r3.id,
        category="Plumbing",
        title="Water tap leaking continuously in washroom",
        description="Cold water faucet handle is loose and water drips continuously.",
        priority="high",
        status="in_progress",
        assigned_to=staff2.id,
        assigned_at=datetime.utcnow() - timedelta(hours=6),
        resolution_notes="Inspected washer; replacing ceramic spindle valve.",
    )
    db.add_all([c1, c2])

    # Notices
    n1 = Notice(
        title="Water Supply Maintenance Schedule - Blocks A & B",
        content="Routine overhead tank cleaning and chlorination will occur on Wednesday, 10:00 AM to 02:00 PM.",
        category="Maintenance",
        priority="urgent",
        target_audience="all",
        is_published=True,
    )
    n2 = Notice(
        title="Annual Cultural Night Registrations Open",
        content="Registrations for inter-hostel cultural competition are now open at the warden office.",
        category="Events",
        priority="normal",
        target_audience="students",
        is_published=True,
    )
    db.add_all([n1, n2])

    # Feedback
    fb1 = MessFeedback(
        student_id=std1.id,
        meal_type="dinner",
        rating=4,
        hygiene_rating=5,
        taste_rating=4,
        comments="Dinner quality was very good today. Clean tables and good portion sizes.",
        date=datetime.utcnow().strftime("%Y-%m-%d"),
    )
    db.add(fb1)

    db.commit()
    print("Database seeding completed.")
