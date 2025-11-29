from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class NodeBase(BaseModel):
    title: str
    slug: str
    category: str
    subcategory: Optional[str] = None
    description: Optional[str] = None
    difficulty_level: int = Field(ge=1, le=5, default=1)
    estimated_time_minutes: Optional[int] = None
    x_position: Optional[float] = None
    y_position: Optional[float] = None
    color: Optional[str] = "#3b82f6"
    icon: Optional[str] = "📚"
    content_path: Optional[str] = None
    extra_metadata: Optional[Dict[str, Any]] = None


class NodeCreate(NodeBase):
    parent_ids: Optional[List[int]] = []


class NodeResponse(NodeBase):
    id: int
    children_ids: List[int] = []
    parent_ids: List[int] = []

    class Config:
        from_attributes = True


class MindMapResponse(BaseModel):
    """Complete mind map structure for visualization"""
    nodes: List[NodeResponse]
    edges: List[Dict[str, Any]]


class QueryRequest(BaseModel):
    node_id: int
    query_type: str = Field(
        default="explanation",
        description="explanation, example, quiz, visualization"
    )
    user_id: str = "demo_user"  # User identifier
    user_context: Optional[str] = None
    force_regenerate: bool = False  # Skip cache if True


class QueryResponse(BaseModel):
    node_title: str
    content_type: str
    generated_content: str
    source_chunks: List[str]
    related_topics: List[str]
    interactive_component: Optional[Dict[str, Any]] = None


class ContentGenerationRequest(BaseModel):
    topic: str
    content_type: str  # explanation, example, quiz, exercise
    difficulty: int = Field(ge=1, le=5, default=3)
    context: Optional[str] = None


class ProgressUpdate(BaseModel):
    user_id: str
    node_id: int
    completed: int = Field(ge=0, le=100)
    quiz_score: Optional[float] = None
    time_spent_minutes: int = 0


class UserCreate(BaseModel):
    user_id: str
    name: Optional[str] = None
    learning_level: int = Field(ge=1, le=5, default=3)
    background: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class UserResponse(BaseModel):
    id: int
    user_id: str
    name: Optional[str]
    learning_level: int
    background: Optional[str]
    preferences: Optional[Dict[str, Any]]
    created_at: datetime
    last_active: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    learning_level: Optional[int] = Field(None, ge=1, le=5)
    background: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class ContentRating(BaseModel):
    """Rating feedback for generated content"""
    generated_content_id: int
    rating: float = Field(ge=1.0, le=5.0)
    feedback: Optional[str] = None


class UsageStats(BaseModel):
    """Usage statistics for admin dashboard"""
    total_users: int
    active_users_24h: int
    total_queries: int
    cache_hit_rate: float
    most_accessed_nodes: List[Dict[str, Any]]
    popular_content_types: Dict[str, int]
    avg_rating_by_difficulty: Dict[int, float]


# Job-Based Personalization Schemas

class JobProfileUpdate(BaseModel):
    """Update user's job target profile"""
    job_title: Optional[str] = None
    job_description: str  # Required for path generation
    job_seniority: Optional[str] = Field(None, description="junior, mid, senior, not_specified")
    firm: Optional[str] = None


class LearningPathStage(BaseModel):
    """Single stage in learning path"""
    stage_name: str
    duration_weeks: int
    description: str
    topics: List[Dict[str, Any]]


class LearningPathResponse(BaseModel):
    """Complete learning path for user"""
    id: int
    user_id: str
    job_description: str
    role_type: str
    stages: List[Dict[str, Any]]
    dependencies: List[Dict[str, Any]] = []
    covered_topics: List[Dict[str, Any]]
    uncovered_topics: List[Dict[str, Any]]
    coverage_percentage: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TopicCoverageCheck(BaseModel):
    """Check if topic is covered in books"""
    topic: str
    covered: bool
    confidence: float
    source: Optional[str] = None
    external_resources: Optional[List[Dict[str, str]]] = None
