from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.models import User, Student
from backend.schemas.schemas import UserCreate, UserLogin, TokenResponse, UserResponse
from backend.services.auth_service import verify_password, get_password_hash, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_data.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    new_user = User(
        email=user_data.email.lower().strip(),
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role if user_data.role in ["student", "warden", "staff"] else "student",
        phone=user_data.phone,
    )
    db.add(new_user)
    db.flush()

    student_profile = None
    if new_user.role == "student":
        student_profile = Student(
            user_id=new_user.id,
            enrollment_no=user_data.enrollment_no or f"STU-{new_user.id[:8].upper()}",
            department=user_data.department or "Engineering",
            year_of_study=user_data.year_of_study or 1,
            gender=user_data.gender or "Other",
        )
        db.add(student_profile)
        db.flush()

    db.commit()
    db.refresh(new_user)

    token = create_access_token(data={"sub": new_user.id, "role": new_user.role})
    return {
        "token": token,
        "user": new_user,
        "studentProfile": student_profile,
        "staffProfile": None,
    }

@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email.lower().strip()).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    student_profile = db.query(Student).filter(Student.user_id == user.id).first() if user.role == "student" else None
    staff_profile = None

    token = create_access_token(data={"sub": user.id, "role": user.role})
    return {
        "token": token,
        "user": user,
        "studentProfile": student_profile,
        "staffProfile": staff_profile,
    }

@router.post("/logout")
def logout():
    return {"message": "Logged out successfully"}
