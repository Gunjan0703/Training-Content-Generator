import os
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import text, func
from sqlalchemy.orm import Session
from langchain_aws import BedrockEmbeddings
from langchain_community.vectorstores import PGVector
from .models import UserWeakness
from .database import get_db

# -------------------------
# Embedding function
# -------------------------
def embeddings():
    return BedrockEmbeddings(
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        model_id=os.getenv("BEDROCK_EMBED_MODEL_ID", "amazon.titan-embed-text-v2:0"),
    )

# -------------------------
# Get PGVector store
# -------------------------
def get_store(collection_name: Optional[str] = None) -> PGVector:
    """
    Connect to Postgres pgvector for user weaknesses in Docker container.
    Connection: postgresql://postgres:root@localhost:5432/temporal_db
    """
    conn = "postgresql://postgres:root@localhost:5432/temporal_db"
    
    return PGVector(
        connection_string=conn,
        collection_name="user_weakness",
        embedding_function=embeddings(),
        distance_strategy="cosine",  # Use cosine similarity
        pre_delete_collection=False,  # Don't delete existing data
        collection_metadata={"hnsw": {"ef_search": 100}},  # Better search quality
    )

# -------------------------
# CRUD Operations
# -------------------------
def save_user_weakness(user_id: str, weakness_text: str) -> Dict[str, Any]:
    """
    Save a user's weakness using SQLAlchemy ORM.
    Returns the created record.
    """
    embed_fn = embeddings()
    vector = embed_fn.embed_query(weakness_text)
    
    for db in get_db():
        try:
            new_weakness = UserWeakness(
                user_id=user_id,
                weakness_text=weakness_text,
                embedding=vector
            )
            db.add(new_weakness)
            db.commit()
            db.refresh(new_weakness)
            return new_weakness.to_dict()
        except Exception as e:
            db.rollback()
            raise

def get_user_weaknesses(user_id: str) -> List[Dict[str, Any]]:
    """Get all weaknesses for a user using SQLAlchemy."""
    for db in get_db():
        weaknesses = db.query(UserWeakness)\
            .filter(UserWeakness.user_id == user_id)\
            .order_by(UserWeakness.created_at.desc())\
            .all()
        return [w.to_dict() for w in weaknesses]

def update_user_weakness(weakness_id: int, weakness_text: str) -> Dict[str, Any]:
    """Update an existing weakness using SQLAlchemy."""
    embed_fn = embeddings()
    vector = embed_fn.embed_query(weakness_text)
    
    for db in get_db():
        try:
            weakness = db.query(UserWeakness).filter(UserWeakness.id == weakness_id).first()
            if not weakness:
                raise ValueError(f"No weakness found with id {weakness_id}")
            
            weakness.weakness_text = weakness_text
            weakness.embedding = vector
            weakness.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(weakness)
            return weakness.to_dict()
        except Exception as e:
            db.rollback()
            raise

def find_similar_weaknesses(query_text: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Find similar weaknesses using vector similarity with SQLAlchemy."""
    try:
        embed_fn = embeddings()
        query_vector = embed_fn.embed_query(query_text)
        
        for db in get_db():
            # First, ensure the table exists and has data
            count = db.query(UserWeakness).count()
            print(f"[DEBUG] Found {count} total weaknesses in database")
            
            if count == 0:
                print("[DEBUG] No weaknesses found in database")
                return []
            
            # Perform similarity search with better scoring using SQLAlchemy
            similarity_cte = text("""
                WITH similarity_scores AS (
                    SELECT 
                        id,
                        user_id,
                        weakness_text,
                        created_at,
                        updated_at,
                        1 - (embedding <=> :query_vector) as similarity
                    FROM user_weakness
                    WHERE 1 - (embedding <=> :query_vector) > 0.3
                )
            """)
            
            # Execute the query using SQLAlchemy
            query = text("""
                SELECT * FROM similarity_scores
                ORDER BY similarity DESC
                LIMIT :limit
            """)
            
            result = db.execute(
                similarity_cte.union(query),
                {"query_vector": query_vector, "limit": limit}
            )
            
            # Convert results to dictionaries
            results = []
            for row in result:
                row_dict = {
                    'id': row.id,
                    'user_id': row.user_id,
                    'weakness_text': row.weakness_text,
                    'created_at': row.created_at.isoformat() if row.created_at else None,
                    'updated_at': row.updated_at.isoformat() if row.updated_at else None,
                    'similarity': round(float(row.similarity), 2)
                }
                results.append(row_dict)
            
            print(f"[DEBUG] Found {len(results)} similar weaknesses with scores: {[r['similarity'] for r in results]}")
            return results
                
    except Exception as e:
        print(f"[ERROR] Error in find_similar_weaknesses: {str(e)}")
        return []

def delete_user_weakness(weakness_id: int) -> bool:
    """Delete a weakness using SQLAlchemy."""
    for db in get_db():
        try:
            weakness = db.query(UserWeakness).filter(UserWeakness.id == weakness_id).first()
            if weakness:
                db.delete(weakness)
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            raise
