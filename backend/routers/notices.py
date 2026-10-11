from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models.models import Notice
from backend.schemas.schemas import NoticeCreate, NoticeUpdate, NoticeResponse

router = APIRouter(prefix="/notices", tags=["Notices"])

@router.get("", response_model=List[NoticeResponse])
def get_notices(db: Session = Depends(get_db)):
    notices = db.query(Notice).filter(Notice.is_published == True).order_by(Notice.created_at.desc()).all()
    return notices

@router.post("", response_model=NoticeResponse, status_code=status.HTTP_201_CREATED)
def create_notice(data: NoticeCreate, db: Session = Depends(get_db)):
    new_n = Notice(
        title=data.title,
        content=data.content,
        category=data.category,
        priority=data.priority,
        target_audience=data.target_audience,
        is_published=True,
    )
    db.add(new_n)
    db.commit()
    db.refresh(new_n)
    return new_n

@router.put("/{id}", response_model=NoticeResponse)
def update_notice(id: str, data: NoticeUpdate, db: Session = Depends(get_db)):
    n = db.query(Notice).filter(Notice.id == id).first()
    if not n:
        raise HTTPException(status_code=404, detail="Notice not found")

    for key, val in data.dict(exclude_unset=True).items():
        setattr(n, key, val)

    db.commit()
    db.refresh(n)
    return n

@router.delete("/{id}")
def delete_notice(id: str, db: Session = Depends(get_db)):
    n = db.query(Notice).filter(Notice.id == id).first()
    if not n:
        raise HTTPException(status_code=404, detail="Notice not found")

    db.delete(n)
    db.commit()
    return {"message": "Notice deleted successfully"}
