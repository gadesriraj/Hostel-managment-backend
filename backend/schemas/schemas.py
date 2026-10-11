from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any
from datetime import datetime

# --- Auth & User Schemas ---
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str = "student"
    phone: Optional[str] = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str
    role: str = "student"
    phone: Optional[str] = None
    enrollment_no: Optional[str] = None
    department: Optional[str] = None
    year_of_study: Optional[int] = 1
    gender: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    token: str
    user: UserResponse
    studentProfile: Optional[Any] = None
    staffProfile: Optional[Any] = None

# --- Student Schemas ---
class StudentBase(BaseModel):
    full_name: str
    email: str
    enrollment_no: str
    department: str
    year_of_study: int
    gender: Optional[str] = None
    emergency_contact: Optional[str] = None
    blood_group: Optional[str] = None
    hostel_name: Optional[str] = "Horizon Hall"

class StudentCreate(StudentBase):
    user_id: str
    room_id: Optional[str] = None

class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    department: Optional[str] = None
    year_of_study: Optional[int] = None
    emergency_contact: Optional[str] = None
    blood_group: Optional[str] = None
    phone: Optional[str] = None

class StudentResponse(StudentBase):
    id: str
    user_id: str
    room_id: Optional[str] = None
    room_number: Optional[str] = None
    block: Optional[str] = None
    floor: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Staff Schemas ---
class StaffResponse(BaseModel):
    id: str
    user_id: str
    employee_id: str
    full_name: str
    email: str
    specialization: str
    phone: Optional[str] = None
    status: str = "available"
    active_tasks_count: Optional[int] = 0
    resolved_tasks_count: Optional[int] = 0

    class Config:
        from_attributes = True

# --- Room Schemas ---
class RoomBase(BaseModel):
    room_number: str
    hostel_name: str = "Horizon Hall"
    block: str = "Block A"
    floor: int = 1
    capacity: int = 2
    type: str = "Standard Double"
    amenities: List[str] = []

class RoomCreate(RoomBase):
    pass

class RoomUpdate(BaseModel):
    room_number: Optional[str] = None
    hostel_name: Optional[str] = None
    block: Optional[str] = None
    floor: Optional[int] = None
    capacity: Optional[int] = None
    type: Optional[str] = None
    status: Optional[str] = None
    amenities: Optional[List[str]] = None

class RoomResponse(RoomBase):
    id: str
    status: str
    current_occupants: Optional[int] = 0
    occupants: Optional[List[Any]] = []

    class Config:
        from_attributes = True

# --- Room Allocation Schemas ---
class AllocationCreate(BaseModel):
    student_id: str
    room_id: str
    allocated_by: Optional[str] = None
    notes: Optional[str] = None

class AllocationResponse(BaseModel):
    id: str
    student_id: str
    room_id: str
    allocated_by: str
    allocation_date: Any
    status: str
    notes: Optional[str] = None

    class Config:
        from_attributes = True

# --- Complaint Schemas ---
class ComplaintBase(BaseModel):
    category: str
    title: str
    description: str
    priority: str = "medium"

class ComplaintCreate(ComplaintBase):
    student_id: str

class ComplaintUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None

class ComplaintResponse(ComplaintBase):
    id: str
    complaint_code: str
    student_id: str
    student_name: str
    room_id: Optional[str] = None
    room_number: Optional[str] = None
    status: str
    assigned_to: Optional[str] = None
    assigned_to_name: Optional[str] = None
    assigned_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Visitor Schemas ---
class VisitorCreate(BaseModel):
    student_id: str
    visitor_name: str
    phone_number: str
    relationship: str
    visit_date: str
    entry_time: str
    expected_exit_time: str
    purpose: Optional[str] = None

class VisitorUpdate(BaseModel):
    status: Optional[str] = None
    rejection_reason: Optional[str] = None
    approved_by: Optional[str] = None
    actual_exit_time: Optional[str] = None

class VisitorResponse(BaseModel):
    id: str
    student_id: str
    student_name: str
    room_number: Optional[str] = None
    visitor_name: str
    phone_number: str
    relationship: str
    visit_date: str
    entry_time: str
    expected_exit_time: str
    actual_exit_time: Optional[str] = None
    purpose: Optional[str] = None
    status: str
    approved_by: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# --- Notice Schemas ---
class NoticeCreate(BaseModel):
    title: str
    content: str
    category: str = "General"
    priority: str = "normal"
    target_audience: str = "all"
    published_by_name: Optional[str] = "Warden Office"

class NoticeUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    target_audience: Optional[str] = None
    is_published: Optional[bool] = None

class NoticeResponse(BaseModel):
    id: str
    title: str
    content: str
    category: str
    priority: str
    target_audience: str
    published_by_name: Optional[str] = None
    is_published: bool
    created_at: datetime

    class Config:
        from_attributes = True

# --- Mess Feedback Schemas ---
class MessFeedbackCreate(BaseModel):
    student_id: str
    meal_type: str
    rating: int = Field(..., ge=1, le=5)
    hygiene_rating: int = Field(4, ge=1, le=5)
    taste_rating: int = Field(4, ge=1, le=5)
    comments: Optional[str] = None
    date: Optional[str] = None

class MessFeedbackResponse(BaseModel):
    id: str
    student_id: str
    student_name: str
    meal_type: str
    rating: int
    hygiene_rating: int
    taste_rating: int
    comments: Optional[str] = None
    date: str
    created_at: datetime

    class Config:
        from_attributes = True
