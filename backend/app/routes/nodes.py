from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.models.database import get_db, Node, node_edges
from app.models.schemas import NodeCreate, NodeResponse, MindMapResponse
from sqlalchemy import select

router = APIRouter(prefix="/api/nodes", tags=["nodes"])


@router.get("/", response_model=List[NodeResponse])
def get_all_nodes(
    category: str = None,
    db: Session = Depends(get_db)
):
    """Get all nodes, optionally filtered by category"""
    query = db.query(Node)

    if category:
        query = query.filter(Node.category == category)

    nodes = query.all()

    # Format response with relationships
    response = []
    for node in nodes:
        response.append({
            **node.__dict__,
            "children_ids": [child.id for child in node.children],
            "parent_ids": [parent.id for parent in node.parents]
        })

    return response


@router.get("/mindmap", response_model=MindMapResponse)
def get_mindmap(
    category: str = None,
    db: Session = Depends(get_db)
):
    """Get complete mind map structure for visualization"""
    query = db.query(Node)

    if category:
        query = query.filter(Node.category == category)

    nodes = query.all()

    # Build nodes list
    nodes_response = []
    edges = []

    for node in nodes:
        nodes_response.append({
            **node.__dict__,
            "children_ids": [child.id for child in node.children],
            "parent_ids": [parent.id for parent in node.parents]
        })

        # Build edges
        for child in node.children:
            edges.append({
                "source": node.id,
                "target": child.id,
                "type": "prerequisite"
            })

    return {
        "nodes": nodes_response,
        "edges": edges
    }


@router.get("/{node_id}", response_model=NodeResponse)
def get_node(
    node_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific node by ID"""
    node = db.query(Node).filter(Node.id == node_id).first()

    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    return {
        **node.__dict__,
        "children_ids": [child.id for child in node.children],
        "parent_ids": [parent.id for parent in node.parents]
    }


@router.post("/", response_model=NodeResponse)
def create_node(
    node_data: NodeCreate,
    db: Session = Depends(get_db)
):
    """Create a new node"""
    # Check if slug already exists
    existing = db.query(Node).filter(Node.slug == node_data.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Node with this slug already exists")

    # Extract parent_ids from request
    parent_ids = node_data.parent_ids if hasattr(node_data, 'parent_ids') else []

    # Create node without parent_ids
    node_dict = node_data.model_dump(exclude={'parent_ids'})
    node = Node(**node_dict)

    # Add parent relationships
    if parent_ids:
        parents = db.query(Node).filter(Node.id.in_(parent_ids)).all()
        node.parents.extend(parents)

    db.add(node)
    db.commit()
    db.refresh(node)

    return {
        **node.__dict__,
        "children_ids": [child.id for child in node.children],
        "parent_ids": [parent.id for parent in node.parents]
    }


@router.put("/{node_id}", response_model=NodeResponse)
def update_node(
    node_id: int,
    node_data: NodeCreate,
    db: Session = Depends(get_db)
):
    """Update an existing node"""
    node = db.query(Node).filter(Node.id == node_id).first()

    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    # Update fields
    for key, value in node_data.model_dump(exclude={'parent_ids'}).items():
        if value is not None:
            setattr(node, key, value)

    # Update parent relationships if provided
    if hasattr(node_data, 'parent_ids') and node_data.parent_ids is not None:
        parents = db.query(Node).filter(Node.id.in_(node_data.parent_ids)).all()
        node.parents = parents

    db.commit()
    db.refresh(node)

    return {
        **node.__dict__,
        "children_ids": [child.id for child in node.children],
        "parent_ids": [parent.id for parent in node.parents]
    }


@router.delete("/{node_id}")
def delete_node(
    node_id: int,
    db: Session = Depends(get_db)
):
    """Delete a node"""
    node = db.query(Node).filter(Node.id == node_id).first()

    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    db.delete(node)
    db.commit()

    return {"message": "Node deleted successfully"}


@router.get("/category/{category}", response_model=List[NodeResponse])
def get_nodes_by_category(
    category: str,
    db: Session = Depends(get_db)
):
    """Get all nodes in a specific category"""
    nodes = db.query(Node).filter(Node.category == category).all()

    response = []
    for node in nodes:
        response.append({
            **node.__dict__,
            "children_ids": [child.id for child in node.children],
            "parent_ids": [parent.id for parent in node.parents]
        })

    return response
