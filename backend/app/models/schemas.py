from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


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
    user_context: Optional[str] = None


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
