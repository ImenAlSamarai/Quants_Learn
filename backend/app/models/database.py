from sqlalchemy import create_engine, Column, Integer, String, Text, Float, ForeignKey, Table, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
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


class UserProgress(Base):
    """Track user learning progress"""
    __tablename__ = 'user_progress'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), index=True)  # Simple user tracking for MVP
    node_id = Column(Integer, ForeignKey('nodes.id'))
    completed = Column(Integer, default=0)  # 0-100 percentage
    quiz_score = Column(Float)
    time_spent_minutes = Column(Integer, default=0)
    extra_metadata = Column(JSON)

    node = relationship('Node')


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
