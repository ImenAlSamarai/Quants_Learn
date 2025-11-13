from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db, UserProgress, Node
from app.models.schemas import ProgressUpdate
from typing import List
from sqlalchemy import func

router = APIRouter(prefix="/api/progress", tags=["progress"])


@router.get("/user/{user_id}")
def get_user_progress(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get all progress for a user"""
    progress_records = db.query(UserProgress).filter(
        UserProgress.user_id == user_id
    ).all()

    # Enrich with node information
    results = []
    for record in progress_records:
        node = db.query(Node).filter(Node.id == record.node_id).first()
        results.append({
            "node_id": record.node_id,
            "node_title": node.title if node else "Unknown",
            "node_category": node.category if node else "Unknown",
            "completed": record.completed,
            "quiz_score": record.quiz_score,
            "time_spent_minutes": record.time_spent_minutes
        })

    # Calculate statistics
    total_nodes = db.query(func.count(Node.id)).scalar()
    completed_nodes = len([r for r in results if r['completed'] == 100])
    avg_quiz_score = sum([r['quiz_score'] for r in results if r['quiz_score']]) / len(results) if results else 0
    total_time = sum([r['time_spent_minutes'] for r in results])

    return {
        "user_id": user_id,
        "progress": results,
        "stats": {
            "total_nodes": total_nodes,
            "completed_nodes": completed_nodes,
            "completion_rate": (completed_nodes / total_nodes * 100) if total_nodes > 0 else 0,
            "average_quiz_score": round(avg_quiz_score, 2),
            "total_time_minutes": total_time
        }
    }


@router.post("/update")
def update_progress(
    progress: ProgressUpdate,
    db: Session = Depends(get_db)
):
    """Update user progress for a node"""
    # Check if node exists
    node = db.query(Node).filter(Node.id == progress.node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    # Check if progress record exists
    existing = db.query(UserProgress).filter(
        UserProgress.user_id == progress.user_id,
        UserProgress.node_id == progress.node_id
    ).first()

    if existing:
        # Update existing record
        existing.completed = progress.completed
        if progress.quiz_score is not None:
            existing.quiz_score = progress.quiz_score
        existing.time_spent_minutes += progress.time_spent_minutes
    else:
        # Create new record
        new_progress = UserProgress(
            user_id=progress.user_id,
            node_id=progress.node_id,
            completed=progress.completed,
            quiz_score=progress.quiz_score,
            time_spent_minutes=progress.time_spent_minutes
        )
        db.add(new_progress)

    db.commit()

    return {"message": "Progress updated successfully"}


@router.get("/user/{user_id}/recommendations")
def get_recommendations(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get personalized topic recommendations based on progress"""
    # Get user's completed nodes
    completed = db.query(UserProgress).filter(
        UserProgress.user_id == user_id,
        UserProgress.completed >= 80
    ).all()

    completed_node_ids = [p.node_id for p in completed]
    completed_nodes = db.query(Node).filter(Node.id.in_(completed_node_ids)).all() if completed_node_ids else []

    # Find nodes that have completed prerequisites
    all_nodes = db.query(Node).all()
    recommendations = []

    for node in all_nodes:
        if node.id in completed_node_ids:
            continue  # Skip already completed

        # Check if prerequisites are met
        parent_ids = [p.id for p in node.parents]
        if parent_ids:
            # Has prerequisites
            prerequisites_met = all(pid in completed_node_ids for pid in parent_ids)
            if prerequisites_met:
                recommendations.append({
                    "node_id": node.id,
                    "title": node.title,
                    "category": node.category,
                    "difficulty": node.difficulty_level,
                    "reason": "Prerequisites completed"
                })
        else:
            # No prerequisites - beginner topics
            if node.difficulty_level <= 2:
                recommendations.append({
                    "node_id": node.id,
                    "title": node.title,
                    "category": node.category,
                    "difficulty": node.difficulty_level,
                    "reason": "Beginner topic"
                })

    # Sort by difficulty
    recommendations.sort(key=lambda x: x['difficulty'])

    return {
        "user_id": user_id,
        "recommendations": recommendations[:10]
    }


@router.delete("/user/{user_id}")
def reset_user_progress(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Reset all progress for a user"""
    db.query(UserProgress).filter(UserProgress.user_id == user_id).delete()
    db.commit()

    return {"message": f"Progress reset for user {user_id}"}


@router.get("/leaderboard")
def get_leaderboard(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get top learners by various metrics"""
    # Get all users with their stats
    users = db.query(UserProgress.user_id).distinct().all()
    user_ids = [u[0] for u in users]

    leaderboard = []
    for user_id in user_ids:
        progress_records = db.query(UserProgress).filter(
            UserProgress.user_id == user_id
        ).all()

        completed_count = len([p for p in progress_records if p.completed == 100])
        avg_score = sum([p.quiz_score for p in progress_records if p.quiz_score]) / len(progress_records) if progress_records else 0
        total_time = sum([p.time_spent_minutes for p in progress_records])

        leaderboard.append({
            "user_id": user_id,
            "completed_nodes": completed_count,
            "average_quiz_score": round(avg_score, 2),
            "total_time_minutes": total_time,
            "score": completed_count * 100 + avg_score * 10  # Combined score
        })

    # Sort by combined score
    leaderboard.sort(key=lambda x: x['score'], reverse=True)

    return {
        "leaderboard": leaderboard[:limit]
    }
