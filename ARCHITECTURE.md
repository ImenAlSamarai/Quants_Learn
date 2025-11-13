# Architecture Documentation

## System Overview

The Quant Learning Platform is a full-stack application that combines interactive visualization, retrieval-augmented generation (RAG), and AI-powered content generation to create an engaging learning experience for aspiring quant researchers.

## Core Components

### 1. Frontend (React + Vite)

**Location**: `/frontend`

**Key Technologies**:
- React 18 for UI components
- Vite for fast development and bundling
- react-force-graph-2d for mind map visualization
- Plotly.js for mathematical visualizations
- Axios for API communication

**Component Hierarchy**:
```
App.jsx
├── Header.jsx (category navigation)
├── MindMapViewer.jsx (force-directed graph)
└── NodePanel.jsx (content display)
    ├── Quiz.jsx (interactive quizzes)
    └── Visualization.jsx (math visualizations)
```

**Data Flow**:
1. User selects category → API request for mind map data
2. User clicks node → API request for content
3. Content displayed with tabs (explanation, examples, quiz, visualization)
4. User interactions update progress via API

### 2. Backend (FastAPI)

**Location**: `/backend/app`

**Architecture Pattern**: Layered Architecture

```
Routes Layer (HTTP handlers)
    ↓
Services Layer (business logic)
    ↓
Data Layer (database models)
```

**Key Modules**:

#### Routes (`/routes`)
- `nodes.py`: Mind map structure and node management
- `content.py`: Content queries and LLM generation
- `progress.py`: User progress tracking

#### Services (`/services`)
- `vector_store.py`: Pinecone integration for embeddings
- `llm_service.py`: OpenAI GPT-4 for content generation

#### Models (`/models`)
- `database.py`: SQLAlchemy ORM models
- `schemas.py`: Pydantic models for API validation

**API Design Philosophy**:
- RESTful endpoints
- JSON request/response
- Automatic validation with Pydantic
- OpenAPI documentation at `/docs`

### 3. Data Storage

#### PostgreSQL (Structured Data)

**Schema**:
```sql
nodes
├── id (primary key)
├── title, slug, category, subcategory
├── description, difficulty_level
├── x_position, y_position (for visualization)
├── content_path, metadata

content_chunks
├── id (primary key)
├── node_id (foreign key)
├── chunk_text
├── chunk_index
├── vector_id (Pinecone reference)

node_edges (many-to-many)
├── parent_id, child_id
├── edge_type (prerequisite, related, advanced)

user_progress
├── id (primary key)
├── user_id, node_id
├── completed (0-100%)
├── quiz_score, time_spent_minutes
```

**Why PostgreSQL**:
- ACID compliance for user data
- Complex queries for relationships
- JSON support for flexible metadata
- Well-established and reliable

#### Pinecone (Vector Database)

**Purpose**: Semantic search and retrieval

**Index Structure**:
- **Dimension**: 1536 (text-embedding-3-small)
- **Metric**: Cosine similarity
- **Metadata**: node_id, category, difficulty, text snippet

**Vector ID Format**: `node_{node_id}_chunk_{chunk_index}`

**Query Flow**:
1. User query → OpenAI embedding
2. Pinecone similarity search → top-k chunks
3. Chunks used as context for LLM
4. LLM generates tailored response

**Why Pinecone**:
- Managed service (no infrastructure management)
- Fast similarity search (< 50ms)
- Scales automatically
- Free tier sufficient for MVP

### 4. AI Services

#### OpenAI Integration

**Models Used**:
- `text-embedding-3-small`: For embedding generation (1536 dimensions)
- `gpt-4-turbo-preview`: For content generation

**Use Cases**:

1. **Embeddings** (`vector_store.py:generate_embedding`):
   ```python
   text → OpenAI API → [0.123, -0.456, ...] (1536-dim vector)
   ```

2. **Explanations** (`llm_service.py:generate_explanation`):
   - Input: Topic + context chunks + difficulty level
   - Output: Conceptual explanation (200-400 words)
   - Temperature: 0.7 (balanced creativity)

3. **Examples** (`llm_service.py:generate_applied_example`):
   - Input: Topic + context chunks
   - Output: JSON with scenario, problem, solution, code
   - Format: Structured JSON for rendering

4. **Quizzes** (`llm_service.py:generate_quiz`):
   - Input: Topic + context + difficulty + num_questions
   - Output: JSON array of questions with explanations
   - Types: Multiple choice, conceptual

5. **Visualizations** (`llm_service.py:generate_visualization_config`):
   - Input: Topic + context
   - Output: JSON config for Plotly.js
   - Includes: Parameters, data generation logic

**Why OpenAI**:
- State-of-the-art quality
- Reliable API
- Good educational content generation
- JSON mode for structured outputs

### 5. Content Pipeline

**Location**: `/backend/scripts/index_content.py`

**Pipeline Stages**:

```
Markdown Files
    ↓
1. Parse (frontmatter + content)
    ↓
2. Chunk (500 chars, 50 char overlap)
    ↓
3. Generate Embeddings (OpenAI)
    ↓
4. Upsert to Pinecone (vectors)
    ↓
5. Store Metadata (PostgreSQL)
```

**Chunking Strategy**:
- **Size**: 500 characters (optimal for semantic coherence)
- **Overlap**: 50 characters (preserve context at boundaries)
- **Method**: Paragraph-aware (don't split mid-sentence)

**Content Format** (Markdown):
```markdown
---
title: Topic Name
category: linear_algebra
subcategory: vectors
difficulty: 1-5
estimated_time: 30
---

# Content here
...
```

**Why This Approach**:
- Markdown: Human-readable, version-controllable, portable
- Chunking: Balance between context and precision
- Frontmatter: Structured metadata for filtering

## Data Flow: User Query to Response

### Scenario: User clicks "Vectors and Spaces" node, selects "Explanation" tab

```
1. Frontend (NodePanel.jsx)
   └─ queryContent(node_id=2, query_type="explanation")

2. API Request (POST /api/content/query)
   └─ {
        "node_id": 2,
        "query_type": "explanation",
        "user_context": null
      }

3. Backend (content.py:query_content)
   ├─ Fetch node from PostgreSQL
   ├─ Build search query: "Vectors and Spaces vector operations spaces..."
   └─ Call vector_store.search(query, node_id=2, top_k=5)

4. Vector Store (vector_store.py:search)
   ├─ Generate query embedding via OpenAI
   ├─ Pinecone similarity search
   └─ Return top 5 matches with metadata

5. LLM Service (llm_service.py:generate_explanation)
   ├─ Extract text from matches
   ├─ Build prompt with context
   ├─ Call GPT-4 with system + user prompt
   └─ Return generated explanation

6. Backend Response
   └─ {
        "node_title": "Vectors and Spaces",
        "content_type": "explanation",
        "generated_content": "Vectors are...",
        "source_chunks": ["...", "..."],
        "related_topics": ["Matrix Operations", ...]
      }

7. Frontend (NodePanel.jsx)
   └─ Render Markdown content with syntax highlighting
```

**Performance**:
- Total time: ~2-3 seconds
- Bottleneck: GPT-4 generation (1.5-2s)
- Optimization: Could cache common queries

## Scalability Considerations

### Current Limitations (MVP)

1. **Concurrent Users**: ~10-50 (single backend instance)
2. **Content Size**: ~1000 nodes max (before Pinecone free tier limits)
3. **API Costs**: $0.50-$2 per 1000 queries (OpenAI)

### Scaling Strategies

#### Horizontal Scaling
- Deploy multiple backend instances behind load balancer
- Use Redis for session management
- Pinecone auto-scales on paid tiers

#### Cost Optimization
1. **Caching**:
   - Redis cache for common queries
   - TTL: 1 hour for generated content
   - Reduces API calls by ~60%

2. **Embeddings**:
   - Pre-compute embeddings during indexing
   - Only re-embed on content changes
   - Use smaller model (text-embedding-3-small vs -large)

3. **LLM**:
   - Use GPT-3.5-turbo for simple queries
   - Reserve GPT-4 for complex explanations
   - Implement streaming for faster perceived performance

4. **Database**:
   - Add indexes on frequently queried fields
   - Use connection pooling
   - Consider read replicas for high traffic

### Security Considerations

**Current Implementation** (MVP):
- Simple user_id tracking (no authentication)
- API open to all (no rate limiting)
- Environment variables for secrets

**Production Requirements**:
1. **Authentication**: JWT tokens, OAuth
2. **Rate Limiting**: 100 req/hour per user
3. **Input Validation**: Sanitize all user inputs
4. **CORS**: Restrict to frontend domain
5. **API Keys**: Rotate regularly, use secrets manager
6. **Database**: SSL connections, encrypted at rest
7. **Monitoring**: Error tracking, usage analytics

## Development Workflow

### Adding New Content

1. **Create Markdown File**:
   ```bash
   content/linear_algebra/new_topic.md
   ```

2. **Update Indexing Script**:
   ```python
   # backend/scripts/index_content.py
   new_id = indexer.index_node(
       title="New Topic",
       category="linear_algebra",
       ...
   )
   ```

3. **Run Indexer**:
   ```bash
   python scripts/index_content.py
   ```

4. **Refresh Frontend**: Node appears automatically

### Adding New Features

1. **Backend**:
   - Add route in `/routes`
   - Implement logic in `/services`
   - Update schemas in `/models/schemas.py`
   - Test with Swagger UI at `/docs`

2. **Frontend**:
   - Add API call in `/services/api.js`
   - Create/update component
   - Import and use in parent component

### Testing Strategy

**Unit Tests**:
- Backend: pytest for services and routes
- Frontend: Jest/Vitest for components

**Integration Tests**:
- API endpoints with test database
- Mock external APIs (OpenAI, Pinecone)

**E2E Tests**:
- Playwright for full user flows
- Test on staging environment

## Performance Optimization

### Frontend

1. **Code Splitting**: Load components on demand
2. **Lazy Loading**: Images and visualizations
3. **Memoization**: React.memo for expensive components
4. **Virtualization**: For long lists of nodes
5. **Service Worker**: Offline caching

### Backend

1. **Connection Pooling**: SQLAlchemy engine
2. **Async Endpoints**: For I/O-bound operations
3. **Batching**: Bulk operations where possible
4. **Indexing**: Database indexes on foreign keys
5. **Query Optimization**: Use EXPLAIN for slow queries

### Database

1. **Indexes**: On node_id, category, user_id
2. **Partitioning**: User progress by date
3. **Archiving**: Old progress data
4. **Materialized Views**: For complex aggregations

## Monitoring and Observability

### Metrics to Track

**Backend**:
- Request latency (p50, p95, p99)
- Error rate (4xx, 5xx)
- Database query time
- External API latency (OpenAI, Pinecone)

**Frontend**:
- Page load time
- Time to interactive
- Component render time
- API call duration

**Business**:
- Daily active users
- Content engagement (clicks per node)
- Quiz completion rate
- Average session duration

### Tools

- **Logging**: Structured JSON logs
- **APM**: Datadog, New Relic, or Sentry
- **Dashboards**: Grafana for metrics
- **Alerts**: On error rates, latency spikes

## Future Enhancements

### Phase 2 Features

1. **Code Execution**:
   - Integrate Jupyter kernels
   - Sandboxed Python environment
   - Real-time code execution

2. **Collaborative Learning**:
   - Discussion forums per topic
   - Peer review system
   - Study groups

3. **Adaptive Learning**:
   - Adjust difficulty based on performance
   - Personalized learning paths
   - Spaced repetition for quizzes

4. **Advanced Visualizations**:
   - WebGL for 3D graphics
   - Real-time data feeds
   - Interactive simulations (Monte Carlo, etc.)

5. **Mobile App**:
   - React Native or Flutter
   - Offline mode with local storage
   - Push notifications

### Technical Debt to Address

1. **Type Safety**: Add TypeScript to frontend
2. **Error Handling**: More graceful error messages
3. **Testing**: Achieve 80%+ code coverage
4. **Documentation**: API docs, component storybook
5. **Accessibility**: WCAG 2.1 AA compliance
6. **Internationalization**: Support multiple languages

## Conclusion

This architecture balances simplicity for MVP development with extensibility for future growth. The modular design allows independent scaling of components, and the tech stack is well-suited for an educational AI application.

**Key Design Decisions**:
1. **Separation of concerns**: Clear boundaries between layers
2. **API-first**: Frontend agnostic backend
3. **AI-augmented**: Human-curated content + AI generation
4. **Interactive**: Hands-on learning, not passive reading
5. **Scalable**: Can handle 100s of users → 1000s with minor changes

**Next Steps**:
1. User testing and feedback
2. Content expansion (ML, DL modules)
3. Performance optimization
4. Production deployment
5. Community building
