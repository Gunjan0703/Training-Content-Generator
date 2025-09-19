import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session

# Database configuration
DATABASE_URL = "postgresql://postgres:root@localhost:5432/temporal_db"

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Enable connection health checks
    pool_size=5,         # Set connection pool size
    max_overflow=10,     # Allow up to 10 connections beyond pool_size
    echo=True           # Log SQL queries (set to False in production)
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)

# Create base class for declarative models
Base = declarative_base()
Base.query = db_session.query_property()

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        # Initialize pgvector extension if not exists
        db.execute(text('CREATE EXTENSION IF NOT EXISTS vector'))
        db.commit()
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database."""
    # Get a raw connection
    conn = engine.raw_connection()
    try:
        # Create extension using raw connection to avoid transaction issues
        with conn.cursor() as cur:
            cur.execute('CREATE EXTENSION IF NOT EXISTS vector')
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise Exception(f"Failed to create vector extension: {str(e)}")
    finally:
        conn.close()

    # Create all tables
    Base.metadata.create_all(bind=engine)
