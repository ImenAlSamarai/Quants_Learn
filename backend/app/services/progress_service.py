"""
Progress Service

Calculates profile completion, interview readiness, and competency levels.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.database import User, UserProgress, UserCompetency, StudySession, Node


class ProgressService:
    """Service for calculating user progress metrics"""

    def __init__(self, db: Session):
        self.db = db

    def get_dashboard_data(self, user_id: str) -> Dict:
        """
        Get all dashboard data for a user

        Returns comprehensive progress information including:
        - Profile completion %
        - Interview readiness score
        - Competencies by category
        - Recent activity
        - Recommended topics
        """
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return None

        # Calculate all metrics
        profile_completion = user.profile_completion_percent
        interview_readiness = self._calculate_interview_readiness(user)
        competencies = self._get_competencies_breakdown(user)
        recent_activity = self._get_recent_activity(user)
        recommended_topics = self._get_recommended_topics(user)
        study_streak = self._get_study_streak(user)

        return {
            'profile': {
                'name': user.name,
                'email': user.email,
                'education_level': user.education_level,
                'current_role': user.current_role,
                'target_roles': user.target_roles or [],
                'completion_percent': profile_completion
            },
            'interview_readiness': interview_readiness,
            'competencies': competencies,
            'recent_activity': recent_activity,
            'recommended_topics': recommended_topics,
            'study_streak_days': study_streak,
            'last_active': user.last_active.isoformat() if user.last_active else None
        }

    def _calculate_interview_readiness(self, user: User) -> int:
        """
        Calculate interview readiness score (0-100)

        Components:
        - Category coverage: 40% (how many categories have progress)
        - Topic completion: 40% (average % across categories)
        - Study consistency: 20% (active last 7 days bonus)
        """
        # Get all categories with nodes
        categories = self.db.query(Node.category).distinct().all()
        categories = [cat[0] for cat in categories if cat[0]]
        total_categories = len(categories)

        if total_categories == 0:
            return 0

        # 1. Category coverage (40 points)
        user_progress = self.db.query(UserProgress).filter(
            UserProgress.user_id == user.user_id,
            UserProgress.completed > 0
        ).all()

        categories_with_progress = set()
        for progress in user_progress:
            node = self.db.query(Node).filter(Node.id == progress.node_id).first()
            if node and node.category:
                categories_with_progress.add(node.category)

        category_coverage = len(categories_with_progress) / total_categories
        category_score = int(category_coverage * 40)

        # 2. Topic completion (40 points)
        # Average completion % across all topics with progress
        if user_progress:
            avg_completion = sum(p.completed for p in user_progress) / len(user_progress)
            completion_score = int((avg_completion / 100) * 40)
        else:
            completion_score = 0

        # 3. Study consistency bonus (20 points)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_sessions = self.db.query(StudySession).filter(
            StudySession.user_id == user.user_id,
            StudySession.completed_at >= seven_days_ago
        ).count()

        # Bonus if studied in last 7 days
        consistency_score = 20 if recent_sessions > 0 else 0

        total_score = category_score + completion_score + consistency_score
        return min(total_score, 100)

    def _get_competencies_breakdown(self, user: User) -> List[Dict]:
        """
        Get competency breakdown by category

        Returns list of:
        - category name
        - completion %
        - level (beginner/intermediate/advanced)
        - topics completed / total
        """
        # Get or create competencies for all categories
        categories = ['statistics', 'probability', 'linear_algebra', 'calculus', 'machine_learning']

        competencies = []
        for category in categories:
            # Get total topics in this category
            total_topics = self.db.query(Node).filter(
                Node.category == category.upper()
            ).count()

            # Get completed topics
            completed_topics = self.db.query(UserProgress).join(Node).filter(
                UserProgress.user_id == user.user_id,
                UserProgress.completed >= 80,  # Consider 80%+ as completed
                Node.category == category.upper()
            ).count()

            # Calculate completion %
            completion_percent = int((completed_topics / total_topics * 100)) if total_topics > 0 else 0

            # Determine level
            if completion_percent < 34:
                level = 'beginner'
            elif completion_percent < 67:
                level = 'intermediate'
            else:
                level = 'advanced'

            competencies.append({
                'category': category,
                'category_display': category.replace('_', ' ').title(),
                'completion_percent': completion_percent,
                'level': level,
                'topics_completed': completed_topics,
                'topics_total': total_topics
            })

        return competencies

    def _get_recent_activity(self, user: User, limit: int = 5) -> List[Dict]:
        """Get recent study activity"""
        recent = self.db.query(UserProgress).filter(
            UserProgress.user_id == user.user_id
        ).order_by(UserProgress.last_accessed.desc()).limit(limit).all()

        activity = []
        for progress in recent:
            node = self.db.query(Node).filter(Node.id == progress.node_id).first()
            if node:
                activity.append({
                    'node_id': node.id,
                    'title': node.title,
                    'category': node.category,
                    'completion': progress.completed,
                    'last_accessed': progress.last_accessed.isoformat() if progress.last_accessed else None
                })

        return activity

    def _get_recommended_topics(self, user: User, limit: int = 3) -> List[Dict]:
        """
        Get recommended next topics based on:
        - Categories with progress but not completed
        - Topics in weak categories
        - Prerequisite chains
        """
        # Get categories with lowest completion %
        competencies = self._get_competencies_breakdown(user)
        competencies.sort(key=lambda x: x['completion_percent'])

        # Get topics from weakest categories that user hasn't started
        recommended = []

        for comp in competencies[:2]:  # Focus on 2 weakest categories
            # Get incomplete topics in this category
            category_topics = self.db.query(Node).filter(
                Node.category == comp['category'].upper()
            ).all()

            for topic in category_topics:
                # Check if user has progress on this topic
                progress = self.db.query(UserProgress).filter(
                    UserProgress.user_id == user.user_id,
                    UserProgress.node_id == topic.id
                ).first()

                if not progress or progress.completed < 100:
                    recommended.append({
                        'node_id': topic.id,
                        'title': topic.title,
                        'category': topic.category,
                        'difficulty': topic.difficulty_level,
                        'estimated_time': topic.estimated_time_minutes
                    })

                if len(recommended) >= limit:
                    break

            if len(recommended) >= limit:
                break

        return recommended

    def _get_study_streak(self, user: User) -> int:
        """Calculate consecutive days studied"""
        # Get all study sessions ordered by date
        sessions = self.db.query(StudySession).filter(
            StudySession.user_id == user.user_id
        ).order_by(StudySession.completed_at.desc()).all()

        if not sessions:
            return 0

        # Count consecutive days
        streak = 0
        current_date = datetime.utcnow().date()

        # Get unique dates
        session_dates = set()
        for session in sessions:
            session_dates.add(session.completed_at.date())

        # Count streak from today backwards
        check_date = current_date
        while check_date in session_dates:
            streak += 1
            check_date -= timedelta(days=1)

        return streak

    def update_competencies(self, user_id: str):
        """Update or create competency records for a user"""
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return

        categories = ['statistics', 'probability', 'linear_algebra', 'calculus', 'machine_learning']

        for category in categories:
            # Get or create competency record
            competency = self.db.query(UserCompetency).filter(
                UserCompetency.user_id == user_id,
                UserCompetency.category == category
            ).first()

            if not competency:
                competency = UserCompetency(
                    user_id=user_id,
                    category=category
                )
                self.db.add(competency)

            # Calculate totals
            total_topics = self.db.query(Node).filter(
                Node.category == category.upper()
            ).count()

            completed_topics = self.db.query(UserProgress).join(Node).filter(
                UserProgress.user_id == user_id,
                UserProgress.completed >= 80,
                Node.category == category.upper()
            ).count()

            # Update competency
            competency.topics_total = total_topics
            competency.topics_completed = completed_topics
            competency.level = competency.level_name  # Use property to calculate level

        self.db.commit()

    def log_study_session(self, user_id: str, node_id: int, duration_seconds: int):
        """Log a study session"""
        session = StudySession(
            user_id=user_id,
            node_id=node_id,
            duration_seconds=duration_seconds,
            completed_at=datetime.utcnow()
        )
        self.db.add(session)
        self.db.commit()

        # Update user's last_active
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if user:
            user.last_active = datetime.utcnow()
            self.db.commit()
