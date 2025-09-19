from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, func, Index, text
from sqlalchemy.dialects.postgresql import ARRAY, BYTEA
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.hybrid import hybrid_property
from ..db import Base, engine, get_db
from langchain_aws import BedrockEmbeddings

class MediaVectorStore(Base):
    """Model for media objects with vector embeddings."""
    __tablename__ = 'media_vectors'

    id = Column(Integer, primary_key=True)
    media_id = Column(Integer, ForeignKey('media_objects.id', ondelete='CASCADE'), nullable=False)
    content_type = Column(String(50), nullable=False)  # 'image', 'audio', 'video'
    description = Column(String, nullable=True)
    embedding = Column(ARRAY(Float), nullable=False)
    meta_data = Column(String, nullable=True)  # JSON string for additional metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), 
                       server_default=func.now(),
                       onupdate=func.now(),
                       nullable=False)
    
    # Add basic index for the embedding column
    __table_args__ = (
        Index('idx_embedding', 'embedding'),
    )
    
    # Relationship to media objects
    media = relationship('MediaObject', backref='vectors')
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'media_id': self.media_id,
            'content_type': self.content_type,
            'description': self.description,
            'metadata': self.meta_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class MediaObject(Base):
    """Model for storing media files."""
    __tablename__ = 'media_objects'

    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    mimetype = Column(String, nullable=False)
    size_bytes = Column(Integer, nullable=False)
    data = Column(BYTEA, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

def get_embeddings():
    """Get embeddings model."""
    return BedrockEmbeddings(
        region_name="us-east-1",
        model_id="amazon.titan-embed-text-v2:0",
    )

class VectorService:
    """Service for managing media vectors."""
    
    def __init__(self):
        self.embedding_model = get_embeddings()
    
    def create_vector(self, db: Session, media_id: int, content_type: str, 
                     description: str, metadata: Optional[str] = None) -> Dict[str, Any]:
        """Create a new vector embedding for media."""
        # Generate embedding from description
        embedding = self.embedding_model.embed_query(description)
        
        vector = MediaVectorStore(
            media_id=media_id,
            content_type=content_type,
            description=description,
            embedding=embedding,
            meta_data=metadata
        )
        db.add(vector)
        db.commit()
        db.refresh(vector)
        
        return vector.to_dict()
    
    def find_similar_media(self, db: Session, query_text: str, 
                          content_type: Optional[str] = None, 
                          limit: int = 5) -> List[Dict[str, Any]]:
        """Find similar media using vector similarity."""
        # Generate query embedding
        query_vector = self.embedding_model.embed_query(query_text)
        
        # Use the built-in vector operators for similarity search
        similarity_query = text("""
            SELECT 
                mv.*,
                1 - (mv.embedding <-> :query_vector::vector) as similarity
            FROM media_vectors mv
            WHERE (:content_type IS NULL OR mv.content_type = :content_type)
            ORDER BY mv.embedding <-> :query_vector::vector
            LIMIT :limit
        """)
        
        # Execute the query with parameters
        results = db.execute(
            similarity_query,
            {
                "query_vector": query_vector,
                "content_type": content_type,
                "limit": limit
            }
        ).fetchall()
        
        # Convert results to dictionaries with similarity scores
        return [{
            'id': row.id,
            'media_id': row.media_id,
            'content_type': row.content_type,
            'description': row.description,
            'metadata': row.meta_data,
            'created_at': row.created_at.isoformat() if row.created_at else None,
            'updated_at': row.updated_at.isoformat() if row.updated_at else None,
            'similarity': float(row.similarity)
        } for row in results]
    
    def update_vector(self, db: Session, vector_id: int, 
                     description: str, metadata: Optional[str] = None) -> Dict[str, Any]:
        """Update vector embedding."""
        vector = db.query(MediaVectorStore).filter(MediaVectorStore.id == vector_id).first()
        if not vector:
            raise ValueError(f"No vector found with id {vector_id}")
        
        # Update embedding and metadata
        embedding = self.embedding_model.embed_query(description)
        vector.description = description
        vector.embedding = embedding
        if metadata:
            vector.metadata = metadata
        
        db.commit()
        db.refresh(vector)
        return vector.to_dict()
    
    def delete_vector(self, db: Session, vector_id: int) -> bool:
        """Delete a vector."""
        vector = db.query(MediaVectorStore).filter(MediaVectorStore.id == vector_id).first()
        if vector:
            db.delete(vector)
            db.commit()
            return True
        return False

# Create service instance
vector_service = VectorService()

# Create tables
Base.metadata.create_all(engine)