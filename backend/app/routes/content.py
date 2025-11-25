from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.database import get_db, Node, GeneratedContent, User
from app.models.schemas import QueryRequest, QueryResponse, ContentGenerationRequest
from app.services.vector_store import vector_store
from app.services.llm_service import llm_service
from app.services.learning_path_service import learning_path_service, COMMON_ROLE_TEMPLATES
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import hashlib

router = APIRouter(prefix="/api/content", tags=["content"])


def get_or_create_user(user_id: str, db: Session) -> User:
    """Get existing user or create new one with default settings"""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        user = User(user_id=user_id)  # No default learning_level
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Update last_active timestamp
        user.last_active = datetime.utcnow()
        db.commit()
    return user


@router.post("/query", response_model=QueryResponse)
def query_content(
    request: QueryRequest,
    db: Session = Depends(get_db)
):
    """
    Query content for a specific node and generate LLM response (with caching)

    Supports multiple query types:
    - explanation: Conceptual explanation
    - example: Applied example in quant finance
    - quiz: Interactive quiz
    - visualization: Interactive visualization config
    """
    # Get node information
    node = db.query(Node).filter(Node.id == request.node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    # Get or create user
    user = get_or_create_user(request.user_id, db)

    # Determine cache key strategy based on user's job profile
    job_profile: Optional[Dict[str, Any]] = None
    cache_key: Optional[str] = None
    use_job_based = False

    if user.job_description and len(user.job_description) > 20:
        # User has job profile - use job-based personalization
        use_job_based = True

        # Parse job if not already in user.job_role_type
        if not user.job_role_type or user.job_role_type == 'other':
            job_profile = learning_path_service.analyze_job_description(user.job_description)
            user.job_role_type = job_profile.get('role_type', 'other')
            db.commit()
        else:
            # Use cached role type
            job_profile = {
                'role_type': user.job_role_type,
                'seniority': user.job_seniority or 'mid',
                'domain_focus': 'quantitative finance',
                'teaching_approach': 'Balance theory and practice for interview prep'
            }

        # Determine cache strategy
        if user.job_role_type in COMMON_ROLE_TEMPLATES:
            cache_key = user.job_role_type  # Template-based caching
        else:
            cache_key = hashlib.md5(user.job_description.encode()).hexdigest()[:16]  # Custom job hash
    else:
        # Fallback: use old difficulty-based system for backward compat
        difficulty_level = user.learning_level or 3
        cache_key = f"difficulty_{difficulty_level}"

    # Get current content version for automatic cache invalidation
    node_version = 1
    if node.extra_metadata and isinstance(node.extra_metadata, dict):
        node_version = node.extra_metadata.get('content_version', 1)

    # Check cache first (unless force_regenerate is True)
    if not request.force_regenerate:
        if use_job_based:
            # Job-based cache lookup
            if user.job_role_type in COMMON_ROLE_TEMPLATES:
                cached = db.query(GeneratedContent).filter(
                    GeneratedContent.node_id == request.node_id,
                    GeneratedContent.content_type == request.query_type,
                    GeneratedContent.role_template_id == cache_key,
                    GeneratedContent.content_version == node_version,
                    GeneratedContent.is_valid == True
                ).first()
            else:
                cached = db.query(GeneratedContent).filter(
                    GeneratedContent.node_id == request.node_id,
                    GeneratedContent.content_type == request.query_type,
                    GeneratedContent.job_profile_hash == cache_key,
                    GeneratedContent.content_version == node_version,
                    GeneratedContent.is_valid == True
                ).first()
        else:
            # Old difficulty-based cache lookup
            cached = db.query(GeneratedContent).filter(
                GeneratedContent.node_id == request.node_id,
                GeneratedContent.content_type == request.query_type,
                GeneratedContent.difficulty_level == difficulty_level,
                GeneratedContent.content_version == node_version,
                GeneratedContent.is_valid == True
            ).first()

        if cached:
            # Cache hit! Increment access count and return cached content
            cached.access_count += 1
            db.commit()

            print(f"✓ Cache HIT: node={request.node_id}, type={request.query_type}, cache_key={cache_key}, version={node_version}")

            return QueryResponse(
                node_title=node.title,
                content_type=request.query_type,
                generated_content=cached.generated_content,
                source_chunks=cached.source_chunks or [],
                related_topics=cached.related_topics or [],
                interactive_component=cached.interactive_component
            )

    # Cache miss - generate new content
    print(f"✗ Cache MISS: node={request.node_id}, type={request.query_type}, cache_key={cache_key}")

    # Retrieve relevant chunks from vector store
    search_query = f"{node.title} {node.description or ''}"
    if request.user_context:
        search_query += f" {request.user_context}"

    matches = vector_store.search(
        query=search_query,
        node_id=request.node_id,
        top_k=5
    )

    # Extract text from matches
    context_chunks = [match['text'] for match in matches]
    source_chunks = [match['text'][:200] + "..." for match in matches]

    # Generate content based on query type
    generated_content = ""
    interactive_component = None

    if request.query_type == "explanation":
        if use_job_based and job_profile:
            # Job-based personalized content
            generated_content = llm_service.generate_explanation_for_job(
                topic=node.title,
                context_chunks=context_chunks,
                job_profile=job_profile,
                user_context=request.user_context
            )
        else:
            # Fallback to difficulty-based
            generated_content = llm_service.generate_explanation(
                topic=node.title,
                context_chunks=context_chunks,
                difficulty=difficulty_level,
                user_context=request.user_context
            )

    elif request.query_type == "example":
        # Note: example generation still uses difficulty for now
        # TODO: Add job-based example generation in future
        example_data = llm_service.generate_applied_example(
            topic=node.title,
            context_chunks=context_chunks,
            domain="quant_finance",
            difficulty=difficulty_level if not use_job_based else 3
        )
        generated_content = f"## {example_data.get('title', 'Applied Example')}\n\n"
        generated_content += f"**Scenario:** {example_data.get('scenario', '')}\n\n"
        generated_content += f"**Problem:** {example_data.get('problem', '')}\n\n"
        generated_content += f"**Solution:**\n{example_data.get('solution', '')}\n\n"

        if example_data.get('code_snippet'):
            generated_content += f"**Code:**\n```python\n{example_data['code_snippet']}\n```\n\n"

        if example_data.get('key_insights'):
            generated_content += "**Key Insights:**\n"
            for insight in example_data['key_insights']:
                generated_content += f"- {insight}\n"

        interactive_component = {
            "type": "code_editor",
            "code": example_data.get('code_snippet', ''),
            "language": "python"
        }

    elif request.query_type == "quiz":
        quiz_data = llm_service.generate_quiz(
            topic=node.title,
            context_chunks=context_chunks,
            difficulty=difficulty_level,
            num_questions=5
        )
        generated_content = "## Interactive Quiz\n\nTest your understanding of the concepts.\n"
        interactive_component = {
            "type": "quiz",
            "questions": quiz_data.get('questions', [])
        }

    elif request.query_type == "visualization":
        viz_config = llm_service.generate_visualization_config(
            topic=node.title,
            context_chunks=context_chunks
        )
        generated_content = f"## {viz_config.get('title', 'Interactive Visualization')}\n\n"
        generated_content += f"{viz_config.get('description', '')}\n\n"
        interactive_component = {
            "type": "visualization",
            "config": viz_config
        }

    else:
        raise HTTPException(status_code=400, detail=f"Unknown query type: {request.query_type}")

    # Get related topics suggestions
    all_nodes = db.query(Node).all()
    all_topics = [n.title for n in all_nodes]
    related_topics = llm_service.suggest_related_topics(
        current_topic=node.title,
        all_topics=all_topics
    )

    # Save to cache for future requests
    if use_job_based:
        # Job-based cache
        if user.job_role_type in COMMON_ROLE_TEMPLATES:
            cached_content = GeneratedContent(
                node_id=request.node_id,
                content_type=request.query_type,
                role_template_id=cache_key,
                generated_content=generated_content,
                interactive_component=interactive_component,
                source_chunks=source_chunks,
                related_topics=related_topics[:5],
                content_version=node_version,
                access_count=1,
                is_valid=True
            )
        else:
            cached_content = GeneratedContent(
                node_id=request.node_id,
                content_type=request.query_type,
                job_profile_hash=cache_key,
                generated_content=generated_content,
                interactive_component=interactive_component,
                source_chunks=source_chunks,
                related_topics=related_topics[:5],
                content_version=node_version,
                access_count=1,
                is_valid=True
            )
    else:
        # Old difficulty-based cache
        cached_content = GeneratedContent(
            node_id=request.node_id,
            content_type=request.query_type,
            difficulty_level=difficulty_level,
            generated_content=generated_content,
            interactive_component=interactive_component,
            source_chunks=source_chunks,
            related_topics=related_topics[:5],
            content_version=node_version,
            access_count=1,
            is_valid=True
        )

    db.add(cached_content)
    db.commit()

    print(f"✓ Content cached: node={request.node_id}, type={request.query_type}, cache_key={cache_key}, version={node_version}")

    return QueryResponse(
        node_title=node.title,
        content_type=request.query_type,
        generated_content=generated_content,
        source_chunks=source_chunks,
        related_topics=related_topics[:5],
        interactive_component=interactive_component
    )


@router.get("/node/{node_id}/summary")
def get_node_summary(
    node_id: int,
    db: Session = Depends(get_db)
):
    """Get a quick summary of node content"""
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    # Retrieve top chunks
    matches = vector_store.search(
        query=node.title,
        node_id=node_id,
        top_k=3
    )

    context_chunks = [match['text'] for match in matches]

    # Generate brief summary
    summary = llm_service.generate_explanation(
        topic=node.title,
        context_chunks=context_chunks,
        difficulty=node.difficulty_level
    )

    return {
        "node_id": node_id,
        "title": node.title,
        "summary": summary,
        "num_chunks": len(matches)
    }


@router.post("/generate")
def generate_custom_content(
    request: ContentGenerationRequest,
    db: Session = Depends(get_db)
):
    """Generate custom content on-demand"""

    if request.content_type == "explanation":
        content = llm_service.generate_explanation(
            topic=request.topic,
            context_chunks=[request.context] if request.context else [],
            difficulty=request.difficulty
        )
    elif request.content_type == "example":
        content = llm_service.generate_applied_example(
            topic=request.topic,
            context_chunks=[request.context] if request.context else []
        )
    elif request.content_type == "quiz":
        content = llm_service.generate_quiz(
            topic=request.topic,
            context_chunks=[request.context] if request.context else [],
            difficulty=request.difficulty
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid content type")

    return {
        "topic": request.topic,
        "content_type": request.content_type,
        "content": content
    }


@router.get("/search")
def search_content(
    query: str,
    category: str = None,
    top_k: int = 10,
    db: Session = Depends(get_db)
):
    """Search across all content"""

    # Build filter
    filter_dict = {}
    if category:
        # Get node IDs in this category
        nodes = db.query(Node).filter(Node.category == category).all()
        node_ids = [n.id for n in nodes]
        if node_ids:
            # Note: Pinecone filters require exact match, so we'll filter results after
            pass

    # Search vector store
    matches = vector_store.search(
        query=query,
        top_k=top_k
    )

    # Enrich results with node information
    results = []
    for match in matches:
        node_id = match['metadata'].get('node_id')
        if node_id:
            node = db.query(Node).filter(Node.id == node_id).first()
            if node and (not category or node.category == category):
                results.append({
                    "node_id": node_id,
                    "node_title": node.title,
                    "node_category": node.category,
                    "text": match['text'],
                    "score": match['score']
                })

    return {
        "query": query,
        "results": results,
        "total": len(results)
    }
