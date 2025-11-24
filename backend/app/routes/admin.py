from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.database import get_db, Node, User, UserProgress, GeneratedContent
from app.models.schemas import UsageStats
from datetime import datetime, timedelta
from typing import List
import os
import shutil
from pathlib import Path

router = APIRouter(prefix="/api/admin", tags=["admin"])

# Content upload directory
CONTENT_DIR = Path(__file__).parent.parent.parent.parent / "content"


@router.get("/stats", response_model=UsageStats)
def get_usage_stats(db: Session = Depends(get_db)):
    """Get platform usage statistics"""

    # Total users
    total_users = db.query(func.count(User.id)).scalar()

    # Active users in last 24h
    yesterday = datetime.utcnow() - timedelta(hours=24)
    active_users_24h = db.query(func.count(User.id)).filter(
        User.last_active >= yesterday
    ).scalar()

    # Total queries (cached content access count)
    total_queries = db.query(func.sum(GeneratedContent.access_count)).scalar() or 0

    # Cache hit rate calculation
    total_cached = db.query(func.count(GeneratedContent.id)).scalar() or 1
    cache_hit_rate = (total_queries - total_cached) / max(total_queries, 1)

    # Most accessed nodes
    most_accessed = db.query(
        Node.id,
        Node.title,
        func.sum(GeneratedContent.access_count).label('access_count')
    ).join(GeneratedContent).group_by(Node.id, Node.title).order_by(
        desc('access_count')
    ).limit(10).all()

    most_accessed_nodes = [
        {"node_id": n.id, "title": n.title, "access_count": n.access_count}
        for n in most_accessed
    ]

    # Popular content types
    content_type_stats = db.query(
        GeneratedContent.content_type,
        func.sum(GeneratedContent.access_count).label('count')
    ).group_by(GeneratedContent.content_type).all()

    popular_content_types = {
        stat.content_type: stat.count for stat in content_type_stats
    }

    # Average rating by difficulty level
    rating_by_difficulty = db.query(
        GeneratedContent.difficulty_level,
        func.avg(GeneratedContent.rating).label('avg_rating')
    ).filter(
        GeneratedContent.rating.isnot(None)
    ).group_by(GeneratedContent.difficulty_level).all()

    avg_rating_by_difficulty = {
        stat.difficulty_level: float(stat.avg_rating) if stat.avg_rating else 0.0
        for stat in rating_by_difficulty
    }

    return UsageStats(
        total_users=total_users,
        active_users_24h=active_users_24h,
        total_queries=total_queries,
        cache_hit_rate=cache_hit_rate,
        most_accessed_nodes=most_accessed_nodes,
        popular_content_types=popular_content_types,
        avg_rating_by_difficulty=avg_rating_by_difficulty
    )


@router.post("/upload-content")
async def upload_content(
    category: str = Form(...),
    file: UploadFile = File(...)
):
    """Upload markdown or PDF content file"""

    # Validate file type
    allowed_extensions = {'.md', '.pdf', '.txt'}
    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_extension} not allowed. Use .md, .pdf, or .txt"
        )

    # Create category directory if it doesn't exist
    category_dir = CONTENT_DIR / category
    category_dir.mkdir(parents=True, exist_ok=True)

    # Save file
    file_path = category_dir / file.filename

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "message": "File uploaded successfully",
        "file_path": str(file_path),
        "category": category,
        "filename": file.filename,
        "next_step": "Run indexing to process this content"
    }


@router.post("/invalidate-cache")
def invalidate_cache(
    node_id: int = None,
    content_type: str = None,
    db: Session = Depends(get_db)
):
    """Invalidate cached content (force regeneration)"""

    query = db.query(GeneratedContent)

    if node_id:
        query = query.filter(GeneratedContent.node_id == node_id)

    if content_type:
        query = query.filter(GeneratedContent.content_type == content_type)

    # Mark as invalid
    count = query.update({"is_valid": False})
    db.commit()

    return {
        "message": f"Invalidated {count} cached entries",
        "node_id": node_id,
        "content_type": content_type
    }


@router.delete("/cache")
def clear_cache(db: Session = Depends(get_db)):
    """Clear all cached content (use with caution!)"""

    count = db.query(GeneratedContent).delete()
    db.commit()

    return {
        "message": f"Cleared {count} cached entries",
        "warning": "All content will be regenerated on next request"
    }


@router.get("/content-library")
def list_content_files():
    """List all content files in the library"""

    if not CONTENT_DIR.exists():
        return {"categories": []}

    categories = []

    for category_dir in CONTENT_DIR.iterdir():
        if category_dir.is_dir():
            files = []
            for file_path in category_dir.iterdir():
                if file_path.is_file() and file_path.suffix in {'.md', '.pdf', '.txt'}:
                    files.append({
                        "filename": file_path.name,
                        "size_kb": file_path.stat().st_size / 1024,
                        "modified": datetime.fromtimestamp(
                            file_path.stat().st_mtime
                        ).isoformat()
                    })

            categories.append({
                "category": category_dir.name,
                "files": files,
                "file_count": len(files)
            })

    return {"categories": categories}


@router.get("/feedback")
def get_student_feedback(
    min_rating: float = None,
    difficulty_level: int = None,
    db: Session = Depends(get_db)
):
    """Get student feedback on generated content"""

    query = db.query(GeneratedContent).filter(
        GeneratedContent.rating.isnot(None)
    )

    if min_rating:
        query = query.filter(GeneratedContent.rating >= min_rating)

    if difficulty_level:
        query = query.filter(GeneratedContent.difficulty_level == difficulty_level)

    feedback = query.order_by(desc(GeneratedContent.created_at)).limit(50).all()

    return {
        "feedback_count": len(feedback),
        "feedback": [
            {
                "node_id": item.node_id,
                "content_type": item.content_type,
                "difficulty_level": item.difficulty_level,
                "rating": item.rating,
                "access_count": item.access_count,
                "created_at": item.created_at.isoformat()
            }
            for item in feedback
        ]
    }
