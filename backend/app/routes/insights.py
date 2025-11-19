"""
API routes for topic insights
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db, TopicInsights, Node
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/insights", tags=["insights"])


class InsightScenario(BaseModel):
    scenario: str
    rationale: str


class InsightLimitation(BaseModel):
    issue: str
    explanation: str
    mitigation: Optional[str] = None


class MethodComparison(BaseModel):
    method_a: str
    method_b: str
    key_difference: str
    when_to_prefer: str


class TopicInsightsResponse(BaseModel):
    node_id: int
    topic_title: str
    when_to_use: List[InsightScenario]
    limitations: List[InsightLimitation]
    practical_tips: List[str]
    method_comparisons: List[MethodComparison]
    computational_notes: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("/{node_id}", response_model=TopicInsightsResponse)
def get_topic_insights(node_id: int, db: Session = Depends(get_db)):
    """
    Get practitioner insights for a specific topic

    Returns structured insights including:
    - When to use this method
    - Limitations and caveats
    - Practical tips
    - Comparisons with related methods
    - Computational considerations
    """

    # Get the node
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Get insights
    insights = db.query(TopicInsights).filter(TopicInsights.node_id == node_id).first()
    if not insights:
        raise HTTPException(status_code=404, detail="Insights not available for this topic yet")

    # Format response
    return TopicInsightsResponse(
        node_id=node_id,
        topic_title=node.title,
        when_to_use=insights.when_to_use or [],
        limitations=insights.limitations or [],
        practical_tips=insights.practical_tips or [],
        method_comparisons=insights.method_comparisons or [],
        computational_notes=insights.computational_notes
    )


@router.get("/check/{node_id}")
def check_insights_available(node_id: int, db: Session = Depends(get_db)):
    """
    Check if insights are available for a topic (lightweight endpoint for UI)
    """
    insights = db.query(TopicInsights).filter(TopicInsights.node_id == node_id).first()
    return {
        "available": insights is not None,
        "node_id": node_id
    }
