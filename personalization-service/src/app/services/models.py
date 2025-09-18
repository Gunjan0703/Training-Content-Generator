from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, func, Index, create_engine
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.hybrid import hybrid_property
from .database import Base

class UserWeakness(Base):
    """Model for user weaknesses with vector embeddings."""
    __tablename__ = 'user_weakness'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=False, index=True)
    weakness_text = Column(String, nullable=False)
    embedding = Column(ARRAY(Float), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), 
                       server_default=func.now(),
                       onupdate=func.now(),
                       nullable=False)
    
    # Add vector similarity index using raw SQL (will be created in migration)
    __table_args__ = (
        Index('vector_l2_idx', 'embedding', postgresql_using='ivfflat',
              postgresql_with={'lists': '100'},
              postgresql_ops={'embedding': 'vector_l2_ops'}),
    )
    
    @hybrid_property
    def embedding_vector(self):
        """Get embedding as a vector."""
        return self.embedding if self.embedding else []
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'weakness_text': self.weakness_text,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Topic(Base):
    """Model for learning topics."""
    __tablename__ = 'topic'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(String, nullable=True)
    embedding = Column(ARRAY(Float), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    weaknesses = relationship('TopicWeakness', back_populates='topic')

class TopicWeakness(Base):
    """Model for topic-weakness relationships with relevance scoring."""
    __tablename__ = 'topic_weakness'
    
    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey('topic.id', ondelete='CASCADE'), nullable=False)
    weakness_id = Column(Integer, ForeignKey('user_weakness.id', ondelete='CASCADE'), nullable=False)
    relevance_score = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    topic = relationship('Topic', back_populates='weaknesses')
    weakness = relationship('UserWeakness')

def get_db_session() -> Session:
    """Create a new database session."""
    # Docker PostgreSQL connection settings
    conn_str = "postgresql://postgres:root@localhost:5432/temporal_db"
    
    engine = create_engine(
        conn_str,
        pool_pre_ping=True,  # Enable connection health checks
        pool_size=5,         # Set connection pool size
        max_overflow=10,     # Allow up to 10 connections beyond pool_size
        echo=True           # Log SQL queries for debugging
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

# Create tables
def init_db():
    """Initialize database tables."""
    conn_str = os.getenv("DATABASE_URL")
    if not conn_str:
        raise RuntimeError("DATABASE_URL is not configured")
    
    engine = create_engine(conn_str)
    
    # Create pgvector extension if it doesn't exist
    with engine.connect() as connection:
        connection.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        connection.commit()
    
    # Create tables
    Base.metadata.create_all(bind=engine)