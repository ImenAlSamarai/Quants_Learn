from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db, User, UserProgress, LearningPath
from app.models.schemas import (
    UserCreate, UserResponse, UserUpdate, ContentRating,
    JobProfileUpdate, LearningPathResponse, TopicCoverageCheck
)
from app.models.database import GeneratedContent
from app.services.progress_service import ProgressService
from app.services.learning_path_service import learning_path_service
from app.utils.cost_tracker import cost_tracker
from typing import List
from fastapi import Header
import os

router = APIRouter(prefix="/api/users", tags=["users"])


def verify_admin_token(x_admin_token: str = Header(None)):
    """Verify admin access - require X-Admin-Token header"""
    if not x_admin_token:
        raise HTTPException(status_code=401, detail="Admin token required. Set X-Admin-Token header.")

    admin_token = os.getenv("ADMIN_TOKEN", "demo-token-change-in-production")
    if x_admin_token != admin_token:
        raise HTTPException(status_code=403, detail="Invalid admin token")
    return True


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


# ============ JOB-BASED PERSONALIZATION ENDPOINTS ============

@router.post("/{user_id}/job-profile")
def update_job_profile(
    user_id: str,
    job_data: JobProfileUpdate,
    db: Session = Depends(get_db)
):
    """
    Update user's job target and generate personalized learning path

    This endpoint:
    1. Saves job profile fields (title, description, seniority, firm)
    2. Analyzes job description to extract role type
    3. Generates complete learning path based on job requirements
    4. Checks topic coverage (Tier 3)
    5. Returns learning path with covered/uncovered topics

    RATE LIMIT: 1 path generation per user per 24 hours (testing/demo protection)
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ============ RATE LIMITING: Prevent API cost explosion ============
    from datetime import datetime, timedelta

    # Rate limit hours (configurable via environment variable)
    rate_limit_hours = int(os.getenv("LEARNING_PATH_RATE_LIMIT_HOURS", "24"))

    # Check if user generated a path in last N hours
    recent_path = db.query(LearningPath).filter(
        LearningPath.user_id == user_id,
        LearningPath.created_at >= datetime.utcnow() - timedelta(hours=rate_limit_hours)
    ).first()

    if recent_path:
        hours_since = (datetime.utcnow() - recent_path.created_at).total_seconds() / 3600
        hours_remaining = rate_limit_hours - hours_since
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit: You can generate 1 learning path per {rate_limit_hours} hours. Try again in {hours_remaining:.1f} hours. (Cost protection during testing)"
        )

    # Update job fields
    user.job_title = job_data.job_title
    user.job_description = job_data.job_description
    user.job_seniority = job_data.job_seniority
    user.firm = job_data.firm

    # ============ DEBUG: Print User Input ============
    print("\n" + "="*80)
    print("📥 USER INPUT RECEIVED")
    print("="*80)
    print(f"User ID: {user_id}")
    print(f"Job Title: {job_data.job_title or 'Not provided'}")
    print(f"Seniority: {job_data.job_seniority or 'Not specified'}")
    print(f"Firm: {job_data.firm or 'Not provided'}")
    print(f"\nJob Description ({len(job_data.job_description)} characters):")
    print("-" * 80)
    print(job_data.job_description)
    print("-" * 80)
    print("="*80 + "\n")

    # Analyze job to extract role type (using GPT-4o-mini)
    print(f"🔍 Analyzing job description for user {user_id}...")
    job_profile = learning_path_service.analyze_job_description(job_data.job_description)
    user.job_role_type = job_profile.get('role_type', 'other')

    db.commit()
    db.refresh(user)

    # Generate learning path (Tier 3 coverage check included)
    print(f"Generating learning path for {user.job_role_type}...")
    try:
        learning_path = learning_path_service.generate_path_for_job(
            job_description=job_data.job_description,
            user_id=user_id,
            db=db
        )
    except Exception as e:
        print(f"Error generating learning path: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate learning path: {str(e)}")

    return {
        "message": "Job profile updated and learning path generated",
        "user": {
            "user_id": user.user_id,
            "job_title": user.job_title,
            "job_role_type": user.job_role_type,
            "profile_completion_percent": user.profile_completion_percent
        },
        "learning_path": {
            "id": learning_path.id,
            "role_type": learning_path.role_type,
            "stages": learning_path.stages,
            "covered_topics": learning_path.covered_topics,
            "uncovered_topics": learning_path.uncovered_topics,
            "coverage_percentage": learning_path.coverage_percentage
        }
    }


@router.get("/{user_id}/learning-path", response_model=LearningPathResponse)
def get_learning_path(user_id: str, db: Session = Depends(get_db)):
    """
    Get user's current learning path

    Returns the most recent learning path generated for this user.
    If no path exists, returns 404.
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get most recent learning path
    learning_path = db.query(LearningPath).filter(
        LearningPath.user_id == user_id
    ).order_by(LearningPath.created_at.desc()).first()

    if not learning_path:
        raise HTTPException(
            status_code=404,
            detail="No learning path found. Please set your job profile first."
        )

    return learning_path


@router.delete("/{user_id}/learning-path")
def delete_learning_path(
    user_id: str,
    db: Session = Depends(get_db),
    _admin: bool = Depends(verify_admin_token)
):
    """
    [ADMIN ONLY] Delete user's learning path to reset rate limit

    Requires X-Admin-Token header for authentication.
    Users must email admin to request learning path deletion.
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Delete all learning paths for this user
    deleted_count = db.query(LearningPath).filter(
        LearningPath.user_id == user_id
    ).delete()

    db.commit()

    return {
        "message": "Learning path deleted successfully",
        "deleted_count": deleted_count,
        "user_id": user_id
    }


@router.post("/check-coverage", response_model=TopicCoverageCheck)
def check_topic_coverage(topic: str, db: Session = Depends(get_db)):
    """
    Check if a specific topic is covered in our books (Tier 3)

    Returns:
    - covered: bool (whether topic is in books)
    - confidence: float (similarity score)
    - source: str (which book, if covered)
    - external_resources: list (if not covered)
    """
    coverage = learning_path_service.check_topic_coverage(topic)

    return TopicCoverageCheck(**coverage)


@router.get("/topics/{topic_name}/structure")
def get_topic_structure(
    topic_name: str,
    keywords: str = "",  # Comma-separated keywords
    db: Session = Depends(get_db)
):
    """
    Get learning structure (weeks/sections) for a topic with smart caching

    Flow:
    1. Check cache - if exists, return instantly (FREE!)
    2. If not cached - generate with GPT-4o-mini + RAG (~$0.006)
    3. Cache for all future users

    Query params:
    - keywords: Optional comma-separated keywords for better RAG retrieval

    Returns:
    - weeks: Array of weeks with sections
    - estimated_hours: Total learning time
    - source_books: Books used
    - cached: Whether this was cached or freshly generated
    """
    # Parse keywords
    keyword_list = [k.strip() for k in keywords.split(",")] if keywords else []

    # Get topic from user's learning path to find source books
    # For now, do a quick coverage check to find source books
    coverage = learning_path_service.check_topic_coverage(topic_name)

    source_books = coverage.get('all_sources', []) if coverage['covered'] else []

    # Get or generate structure (cache-first!)
    structure = learning_path_service.get_or_generate_topic_structure(
        topic_name=topic_name,
        keywords=keyword_list,
        source_books=source_books,
        db=db
    )

    return structure


@router.get("/topics/{topic_name}/sections/{section_id}/content")
def get_section_content(
    topic_name: str,
    section_id: str,
    section_title: str = "",
    keywords: str = "",  # Comma-separated keywords
    db: Session = Depends(get_db)
):
    """
    Get rich learning content for a specific section using Claude API

    Uses Claude Sonnet 3.5 for premium-quality content generation
    Falls back to GPT-4 if Claude unavailable
    Caches content for instant retrieval on subsequent requests

    Flow:
    1. Check cache - if exists, return instantly (FREE!)
    2. If not cached - generate with Claude + RAG (~$0.02-0.05)
    3. Cache for all future users

    Query params:
    - section_title: Required - the section title
    - keywords: Optional comma-separated keywords for better RAG retrieval

    Returns:
    - content: Rich markdown with LaTeX, code examples, interview tips
    - estimated_minutes: Reading time
    - cached: Whether this was cached or freshly generated
    - generation_model: Which model generated the content
    """
    if not section_title:
        return {"error": "section_title query parameter is required"}

    # Parse keywords
    keyword_list = [k.strip() for k in keywords.split(",")] if keywords else []

    # Get or generate section content (cache-first!)
    result = learning_path_service.get_or_generate_section_content(
        topic_name=topic_name,
        section_id=section_id,
        section_title=section_title,
        topic_keywords=keyword_list,
        db=db
    )

    return result


@router.get("/admin/api-costs", dependencies=[Depends(verify_admin_token)])
def get_api_costs():
    """
    Admin endpoint to monitor API usage and costs

    Returns daily and total costs to prevent budget overrun during testing
    """
    stats = cost_tracker.get_stats()

    return {
        "daily_cost_usd": round(stats.get('daily_cost', 0), 2),
        "daily_calls": stats.get('daily_calls', 0),
        "daily_budget_usd": stats.get('daily_budget', 10.0),
        "budget_remaining_usd": round(stats.get('budget_remaining', 0), 2),
        "total_cost_usd": round(stats.get('total_cost', 0), 2),
        "total_calls": stats.get('total_calls', 0),
        "by_model": stats.get('by_model', {}),
        "by_operation": stats.get('by_operation', {}),
        "warning": "🚨 TESTING MODE: Monitor costs closely!" if stats.get('daily_cost', 0) > 5 else None
    }
