import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    Text,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
    JSON,
    Float
)
from sqlalchemy.orm import relationship
from backend.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class UserRole:
    STUDENT = "student"
    WARDEN = "warden"
    STAFF = "staff"

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=False)
    role = Column(String(20), nullable=False, default=UserRole.STUDENT)
    phone = Column(String(30), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student_profile = relationship("Student", back_populates="user", uselist=False, cascade="all, delete-orphan")
    staff_profile = relationship("Staff", back_populates="user", uselist=False, cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


class Student(Base):
    __tablename__ = "students"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    enrollment_no = Column(String(50), unique=True, index=True, nullable=False)
    department = Column(String(100), nullable=False)
    year_of_study = Column(Integer, default=1)
    gender = Column(String(20), nullable=True)
    emergency_contact = Column(String(100), nullable=True)
    blood_group = Column(String(10), nullable=True)
    room_id = Column(String(36), ForeignKey("rooms.id", ondelete="SET NULL"), nullable=True)
    hostel_name = Column(String(100), default="Horizon Hall")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="student_profile")
    room = relationship("Room", back_populates="residents")
    allocations = relationship("RoomAllocation", back_populates="student", cascade="all, delete-orphan")
    complaints = relationship("Complaint", back_populates="student", cascade="all, delete-orphan")
    visitors = relationship("Visitor", back_populates="student", cascade="all, delete-orphan")
    feedbacks = relationship("MessFeedback", back_populates="student", cascade="all, delete-orphan")


class Staff(Base):
    __tablename__ = "staff"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    employee_id = Column(String(50), unique=True, index=True, nullable=False)
    specialization = Column(String(100), nullable=False) # Electrical, Plumbing, Carpentry, etc.
    phone = Column(String(30), nullable=True)
    status = Column(String(20), default="available") # available, busy, off_duty
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="staff_profile")
    assigned_complaints = relationship("Complaint", back_populates="assigned_staff")


class Room(Base):
    __tablename__ = "rooms"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    room_number = Column(String(30), unique=True, index=True, nullable=False)
    hostel_name = Column(String(100), nullable=False, default="Horizon Hall")
    block = Column(String(50), nullable=False, default="Block A")
    floor = Column(Integer, nullable=False, default=1)
    capacity = Column(Integer, nullable=False, default=2)
    type = Column(String(50), default="Standard Double")
    status = Column(String(30), default="available") # available, partially_occupied, full, maintenance
    amenities = Column(JSON, default=list) # e.g. ["Wi-Fi", "Study Table", "Balcony"]
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    residents = relationship("Student", back_populates="room")
    allocations = relationship("RoomAllocation", back_populates="room")
    complaints = relationship("Complaint", back_populates="room")


class RoomAllocation(Base):
    __tablename__ = "room_allocations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    room_id = Column(String(36), ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False)
    allocated_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    allocation_date = Column(DateTime, default=datetime.utcnow)
    vacated_date = Column(DateTime, nullable=True)
    status = Column(String(20), default="active") # active, vacated, transferred
    notes = Column(Text, nullable=True)

    # Relationships
    student = relationship("Student", back_populates="allocations")
    room = relationship("Room", back_populates="allocations")


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    complaint_code = Column(String(50), unique=True, index=True, nullable=False)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    room_id = Column(String(36), ForeignKey("rooms.id", ondelete="SET NULL"), nullable=True)
    category = Column(String(50), nullable=False) # Plumbing, Electrical, Carpentry, Cleaning, Wi-Fi, Other
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String(20), default="medium") # low, medium, high, urgent
    status = Column(String(20), default="pending") # pending, assigned, in_progress, resolved, rejected
    assigned_to = Column(String(36), ForeignKey("staff.id", ondelete="SET NULL"), nullable=True)
    assigned_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="complaints")
    room = relationship("Room", back_populates="complaints")
    assigned_staff = relationship("Staff", back_populates="assigned_complaints")
    assignments = relationship("ComplaintAssignment", back_populates="complaint", cascade="all, delete-orphan")


class ComplaintAssignment(Base):
    __tablename__ = "complaint_assignments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    complaint_id = Column(String(36), ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False)
    staff_id = Column(String(36), ForeignKey("staff.id", ondelete="CASCADE"), nullable=False)
    assigned_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(30), default="assigned")
    notes = Column(Text, nullable=True)

    complaint = relationship("Complaint", back_populates="assignments")


class Visitor(Base):
    __tablename__ = "visitors"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    visitor_name = Column(String(100), nullable=False)
    phone_number = Column(String(30), nullable=False)
    relationship = Column(String(50), nullable=False) # Parent, Sibling, Relative, Friend
    visit_date = Column(String(20), nullable=False)
    entry_time = Column(String(10), nullable=False)
    expected_exit_time = Column(String(10), nullable=False)
    actual_exit_time = Column(String(10), nullable=True)
    purpose = Column(String(255), nullable=True)
    status = Column(String(20), default="pending") # pending, approved, rejected, completed
    approved_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="visitors")


class Notice(Base):
    __tablename__ = "notices"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(50), default="General") # General, Maintenance, Rules & Regulations, Events, Emergency
    priority = Column(String(20), default="normal") # normal, important, urgent
    target_audience = Column(String(20), default="all") # all, students, staff
    published_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MessFeedback(Base):
    __tablename__ = "mess_feedback"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    meal_type = Column(String(20), nullable=False) # breakfast, lunch, snacks, dinner
    rating = Column(Integer, nullable=False) # 1-5
    hygiene_rating = Column(Integer, default=4)
    taste_rating = Column(Integer, default=4)
    comments = Column(Text, nullable=True)
    date = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="feedbacks")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), default="system")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")
