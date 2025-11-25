from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db, User, UserProgress
from app.models.schemas import UserCreate, UserResponse, UserUpdate, ContentRating
from app.models.database import GeneratedContent
from app.services.progress_service import ProgressService
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


@router.get("/{user_id}/dashboard")
def get_user_dashboard(user_id: str, db: Session = Depends(get_db)):
    """
    Get comprehensive dashboard data for user

    Returns:
    - Profile completion %
    - Interview readiness score
    - Competencies breakdown by category
    - Recent activity
    - Recommended next topics
    - Study streak
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    progress_service = ProgressService(db)
    dashboard_data = progress_service.get_dashboard_data(user_id)

    if not dashboard_data:
        raise HTTPException(status_code=404, detail="Dashboard data not available")

    return dashboard_data


@router.patch("/{user_id}/profile")
def update_user_profile(user_id: str, updates: dict, db: Session = Depends(get_db)):
    """Update user professional profile fields"""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Allowed profile fields
    allowed_fields = [
        'name', 'email', 'phone', 'cv_url', 'linkedin_url',
        'education_level', 'job_role', 'years_experience', 'target_roles'
    ]

    # Update only allowed fields
    for key, value in updates.items():
        if key in allowed_fields:
            setattr(user, key, value)

    db.commit()
    db.refresh(user)

    # Return updated profile with completion %
    return {
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email,
        "education_level": user.education_level,
        "job_role": user.job_role,
        "profile_completion_percent": user.profile_completion_percent
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
