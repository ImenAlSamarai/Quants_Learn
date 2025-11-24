from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db, User, UserProgress
from app.models.schemas import UserCreate, UserResponse, UserUpdate, ContentRating
from app.models.database import GeneratedContent
from typing import List

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user account"""
    # Check if user already exists
    existing = db.query(User).filter(User.user_id == user.user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str, db: Session = Depends(get_db)):
    """Get user profile"""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(user_id: str, updates: UserUpdate, db: Session = Depends(get_db)):
    """Update user preferences (including learning level)"""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update only provided fields
    update_data = updates.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


@router.get("/{user_id}/progress")
def get_user_progress(user_id: str, db: Session = Depends(get_db)):
    """Get user's learning progress"""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    progress = db.query(UserProgress).filter(UserProgress.user_id == user_id).all()

    return {
        "user_id": user_id,
        "learning_level": user.learning_level,
        "background": user.background,
        "progress": [
            {
                "node_id": p.node_id,
                "completed": p.completed,
                "quiz_score": p.quiz_score,
                "time_spent_minutes": p.time_spent_minutes,
                "last_accessed": p.last_accessed
            }
            for p in progress
        ]
    }


@router.post("/rate-content")
def rate_content(rating: ContentRating, db: Session = Depends(get_db)):
    """Rate generated content (helps improve quality)"""
    content = db.query(GeneratedContent).filter(
        GeneratedContent.id == rating.generated_content_id
    ).first()

    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    content.rating = rating.rating
    db.commit()

    return {
        "message": "Rating saved",
        "content_id": rating.generated_content_id,
        "rating": rating.rating
    }
