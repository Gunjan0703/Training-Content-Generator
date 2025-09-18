import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .models import Base

def init_database():
    """Initialize the database with pgvector extension and required tables."""
    try:
        # Docker PostgreSQL connection settings
        conn_str = "postgresql://postgres:root@localhost:5432/temporal_db"
        engine = create_engine(conn_str, echo=True)
        
        # Drop existing tables to ensure clean initialization
        print("Dropping existing tables...")
        Base.metadata.drop_all(bind=engine)
        
        # Create pgvector extension first
        print("Creating pgvector extension...")
        with engine.connect() as connection:
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            connection.commit()
        
        # Create all tables from models
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        # Create vector similarity index
        print("Creating vector similarity index...")
        with engine.connect() as connection:
            # Create optimized index for vector similarity search
            connection.execute(text("""
                CREATE INDEX IF NOT EXISTS user_weakness_embedding_idx 
                ON user_weakness 
                USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100);
            """))
            connection.commit()
        
        print("Database initialization completed successfully")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

if __name__ == "__main__":
    init_database()