from sqlalchemy import create_engine, Column, Integer, String, Text, Float, ForeignKey, Table, JSON, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from app.config.settings import settings

Base = declarative_base()

# Association table for node relationships (edges)
node_edges = Table(
    'node_edges',
    Base.metadata,
    Column('parent_id', Integer, ForeignKey('nodes.id'), primary_key=True),
    Column('child_id', Integer, ForeignKey('nodes.id'), primary_key=True),
    Column('edge_type', String(50), default='prerequisite')  # prerequisite, related, advanced
)


class Node(Base):
    """Represents a topic/concept node in the mind map"""
    __tablename__ = 'nodes'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    slug = Column(String(200), unique=True, nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)  # linear_algebra, calculus, etc.
    subcategory = Column(String(100))  # vectors, matrices, etc.
    description = Column(Text)
    difficulty_level = Column(Integer, default=1)  # 1-5
    estimated_time_minutes = Column(Integer)
    x_position = Column(Float)  # For mind map visualization
    y_position = Column(Float)
    color = Column(String(20))  # Hex color for the node
    icon = Column(String(50))  # Emoji or icon name
    content_path = Column(String(500))  # Path to markdown file
    extra_metadata = Column(JSON)  # Additional flexible metadata

    # Relationships
    children = relationship(
        'Node',
        secondary=node_edges,
        primaryjoin=id == node_edges.c.parent_id,
        secondaryjoin=id == node_edges.c.child_id,
        backref='parents'
    )

    content_chunks = relationship('ContentChunk', back_populates='node', cascade='all, delete-orphan')

    # Learning path helper properties (stored in extra_metadata)
    @property
    def learning_path(self):
        """Get learning path from metadata"""
        if not self.extra_metadata:
            return None
        return self.extra_metadata.get('learning_path')

    @learning_path.setter
    def learning_path(self, value):
        """Set learning path in metadata"""
        if not self.extra_metadata:
            self.extra_metadata = {}
        self.extra_metadata['learning_path'] = value

    @property
    def sequence_order(self):
        """Get sequence order within learning path"""
        if not self.extra_metadata:
            return None
        return self.extra_metadata.get('sequence_order')

    @sequence_order.setter
    def sequence_order(self, value):
        """Set sequence order in metadata"""
        if not self.extra_metadata:
            self.extra_metadata = {}
        self.extra_metadata['sequence_order'] = value

    @property
    def prerequisites_ids(self):
        """Get list of prerequisite node IDs"""
        if not self.extra_metadata:
            return []
        return self.extra_metadata.get('prerequisites_ids', [])

    @prerequisites_ids.setter
    def prerequisites_ids(self, value):
        """Set prerequisite node IDs"""
        if not self.extra_metadata:
            self.extra_metadata = {}
        self.extra_metadata['prerequisites_ids'] = value if value else []

    @property
    def tags(self):
        """Get topic tags"""
        if not self.extra_metadata:
            return []
        return self.extra_metadata.get('tags', [])

    @tags.setter
    def tags(self, value):
        """Set topic tags"""
        if not self.extra_metadata:
            self.extra_metadata = {}
        self.extra_metadata['tags'] = value if value else []


class ContentChunk(Base):
    """Represents indexed content chunks for RAG"""
    __tablename__ = 'content_chunks'

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(Integer, ForeignKey('nodes.id'), nullable=False)
    chunk_text = Column(Text, nullable=False)
    chunk_index = Column(Integer)  # Order within the document
    vector_id = Column(String(100), unique=True)  # Pinecone vector ID
    extra_metadata = Column(JSON)  # chunk_type: explanation, example, formula, etc.

    node = relationship('Node', back_populates='content_chunks')


class User(Base):
    """User accounts with learning preferences and professional profile"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, nullable=False, index=True)  # Username or email
    name = Column(String(200))
    learning_level = Column(Integer, default=3)  # DEPRECATED: Keep for backward compat with scripts
    background = Column(Text)  # DEPRECATED: Replaced by job_description
    preferences = Column(JSON)  # Custom preferences
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)

    # Phase 2: Professional Profile Fields
    email = Column(String(200))
    phone = Column(String(50))
    cv_url = Column(String(500))  # URL to CV/resume
    linkedin_url = Column(String(500))
    education_level = Column(String(50))  # 'undergraduate', 'masters', 'phd', 'postdoc'
    job_role = Column(String(200))  # Current job title/role
    years_experience = Column(Integer)  # Years of professional experience
    target_roles = Column(JSON)  # Array of target roles: ["quant researcher", "quant trader", etc.]

    # Job-Based Personalization Fields (Phase 2.5)
    job_title = Column(String(200))  # e.g., "Quantitative Researcher"
    job_description = Column(Text)  # Full job posting text
    job_seniority = Column(String(50))  # 'junior', 'mid', 'senior', 'not_specified'
    firm = Column(String(200))  # e.g., "Citadel", "Two Sigma" (optional)
    job_role_type = Column(String(100))  # 'quant_researcher', 'quant_trader', 'risk_quant', 'ml_engineer'

    progress = relationship('UserProgress', back_populates='user')
    competencies = relationship('UserCompetency', back_populates='user', cascade='all, delete-orphan')
    study_sessions = relationship('StudySession', back_populates='user', cascade='all, delete-orphan')

    @property
    def profile_completion_percent(self):
        """Calculate profile completion percentage"""
        total_fields = 4  # name, email, education_level, job_description
        completed = 0

        if self.name:
            completed += 1
        if self.email:
            completed += 1
        if self.education_level:
            completed += 1
        if self.job_description and len(self.job_description) > 20:
            completed += 1

        # Bonus fields (don't count toward base 100%)
        bonus = 0
        if self.cv_url:
            bonus += 5
        if self.linkedin_url:
            bonus += 5
        if self.job_role:
            bonus += 5
        if self.target_roles and len(self.target_roles) > 0:
            bonus += 5

        base_percent = int((completed / total_fields) * 100)
        return min(base_percent + bonus, 100)


class UserProgress(Base):
    """Track user learning progress"""
    __tablename__ = 'user_progress'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), ForeignKey('users.user_id'), index=True)
    node_id = Column(Integer, ForeignKey('nodes.id'))
    completed = Column(Integer, default=0)  # 0-100 percentage
    quiz_score = Column(Float)
    time_spent_minutes = Column(Integer, default=0)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    extra_metadata = Column(JSON)

    user = relationship('User', back_populates='progress')
    node = relationship('Node')


class GeneratedContent(Base):
    """Cache for LLM-generated content"""
    __tablename__ = 'generated_content'

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(Integer, ForeignKey('nodes.id'), nullable=False, index=True)
    content_type = Column(String(50), nullable=False, index=True)  # explanation, example, quiz, visualization
    difficulty_level = Column(Integer, index=True)  # DEPRECATED: Keep for backward compat, nullable now
    generated_content = Column(Text, nullable=False)
    interactive_component = Column(JSON)  # For quizzes, visualizations, etc.
    source_chunks = Column(JSON)  # Track which chunks were used
    related_topics = Column(JSON)  # Suggested related topics
    content_version = Column(Integer, default=1)  # For cache invalidation
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    access_count = Column(Integer, default=0)  # Track usage
    rating = Column(Float)  # Student feedback rating
    is_valid = Column(Boolean, default=True)  # For cache invalidation

    # Job-Based Cache Keys (Phase 2.5)
    role_template_id = Column(String(50), index=True)  # For common roles: 'quant_researcher', 'quant_trader'
    job_profile_hash = Column(String(32), index=True)  # MD5 hash of custom job description

    node = relationship('Node')


class TopicInsights(Base):
    """Practitioner insights extracted from ESL book discussions and bibliographic notes"""
    __tablename__ = 'topic_insights'

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(Integer, ForeignKey('nodes.id'), nullable=False, unique=True, index=True)

    # Structured insights (JSON arrays)
    when_to_use = Column(JSON)  # [{"scenario": "...", "rationale": "..."}]
    limitations = Column(JSON)  # [{"issue": "...", "explanation": "...", "mitigation": "..."}]
    practical_tips = Column(JSON)  # ["tip1", "tip2", ...]
    method_comparisons = Column(JSON)  # [{"method_a": "...", "method_b": "...", "difference": "...", "when_to_prefer": "..."}]
    computational_notes = Column(Text)

    # Raw content from book
    bibliographic_notes = Column(Text)
    discussion_sections = Column(JSON)  # Array of discussion text

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    node = relationship('Node', backref='insights')


class UserCompetency(Base):
    """Track user competency/mastery level per category"""
    __tablename__ = 'user_competencies'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), ForeignKey('users.user_id'), index=True)
    category = Column(String(100), nullable=False, index=True)  # statistics, probability, etc.
    topics_completed = Column(Integer, default=0)  # Number of topics completed in this category
    topics_total = Column(Integer, default=0)  # Total topics in this category at user's level
    level = Column(String(50))  # 'beginner', 'intermediate', 'advanced'
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship('User', back_populates='competencies')

    @property
    def completion_percent(self):
        """Calculate completion percentage for this category"""
        if self.topics_total == 0:
            return 0
        return int((self.topics_completed / self.topics_total) * 100)

    @property
    def level_name(self):
        """Determine competency level based on completion"""
        percent = self.completion_percent
        if percent < 34:
            return 'beginner'
        elif percent < 67:
            return 'intermediate'
        else:
            return 'advanced'


class StudySession(Base):
    """Track individual study sessions for time analytics"""
    __tablename__ = 'study_sessions'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), ForeignKey('users.user_id'), index=True)
    node_id = Column(Integer, ForeignKey('nodes.id'))
    duration_seconds = Column(Integer, default=0)  # Time spent in seconds
    completed_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship('User', back_populates='study_sessions')
    node = relationship('Node')


class LearningPath(Base):
    """Auto-generated learning paths based on job requirements"""
    __tablename__ = 'learning_paths'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), ForeignKey('users.user_id'), index=True)
    job_description = Column(Text)
    role_type = Column(String(100))  # Extracted role type: 'quant_researcher', 'quant_trader', etc.

    # Path structure (JSON)
    stages = Column(JSON)  # [{"stage_name": "...", "topics": [...], "duration_weeks": 2, ...}]
    dependencies = Column(JSON)  # [{"from": "topic1", "to": "topic2", "reason": "why"}]

    # Coverage analysis (Tier 3)
    covered_topics = Column(JSON)  # Topics available in our books: [{"topic": "...", "source": "ESL", ...}]
    uncovered_topics = Column(JSON)  # Topics not in books: [{"topic": "...", "external_resources": [...]}]
    coverage_percentage = Column(Integer)  # 0-100: % of job requirements covered by our books

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship('User', backref='learning_paths')


class TopicStructure(Base):
    """Cached learning structures (weeks/sections) for topics"""
    __tablename__ = 'topic_structures'

    id = Column(Integer, primary_key=True, index=True)
    topic_name = Column(String(200), nullable=False, index=True)  # e.g., "algorithmic strategies"
    topic_hash = Column(String(32), nullable=False, unique=True, index=True)  # MD5(topic_name + keywords) for uniqueness

    # Structure (JSON)
    weeks = Column(JSON, nullable=False)  # [{"weekNumber": 1, "title": "...", "sections": [...]}]

    # Metadata
    keywords = Column(JSON)  # Keywords used for RAG retrieval
    source_books = Column(JSON)  # Books used: [{"source": "ESL", "confidence": 0.85}]
    estimated_hours = Column(Integer)  # Total estimated learning hours
    difficulty_level = Column(Integer, default=3)  # 1-5 scale

    # Caching
    generation_model = Column(String(50), default="gpt-4o-mini")  # Model used for generation
    content_version = Column(Integer, default=1)  # For cache invalidation
    access_count = Column(Integer, default=0)  # Track usage
    is_valid = Column(Boolean, default=True)  # For cache invalidation

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Database setup
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for FastAPI routes"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
