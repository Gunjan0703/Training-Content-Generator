from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from .database import get_db
from .models import UserWeakness, Topic, TopicWeakness
from langchain_aws import BedrockEmbeddings

def get_embeddings():
    """Get embeddings model."""
    return BedrockEmbeddings(
        region_name="us-east-1",
        model_id="amazon.titan-embed-text-v2:0",
    )

class WeaknessService:
    """Service for managing user weaknesses."""
    
    def __init__(self):
        self.embedding_model = get_embeddings()
    
    def create_weakness(self, db: Session, user_id: str, weakness_text: str) -> Dict[str, Any]:
        """Create a new weakness with vector embedding."""
        # Generate embedding
        embedding = self.embedding_model.embed_query(weakness_text)
        
        # Create weakness
        weakness = UserWeakness(
            user_id=user_id,
            weakness_text=weakness_text,
            embedding=embedding
        )
        db.add(weakness)
        db.commit()
        db.refresh(weakness)
        
        return weakness.to_dict()
    
    def get_user_weaknesses(self, db: Session, user_id: str) -> List[Dict[str, Any]]:
        """Get all weaknesses for a user."""
        weaknesses = db.query(UserWeakness)\
            .filter(UserWeakness.user_id == user_id)\
            .order_by(UserWeakness.created_at.desc())\
            .all()
        return [w.to_dict() for w in weaknesses]
    
    def find_similar_weaknesses(self, db: Session, query_text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find similar weaknesses using vector similarity."""
        # Generate query embedding
        query_vector = self.embedding_model.embed_query(query_text)
        
        # Calculate cosine similarity using dot product
        similarities = db.query(
            UserWeakness,
            func.dot(UserWeakness.embedding, query_vector).label('similarity')
        )\
            .filter(func.dot(UserWeakness.embedding, query_vector) > 0.3)\
            .order_by(func.dot(UserWeakness.embedding, query_vector).desc())\
            .limit(limit)\
            .all()
        
        return [{
            **weakness.to_dict(),
            'similarity': float(similarity)
        } for weakness, similarity in similarities]
    
    def update_weakness(self, db: Session, weakness_id: int, weakness_text: str) -> Dict[str, Any]:
        """Update a weakness and its embedding."""
        weakness = db.query(UserWeakness).filter(UserWeakness.id == weakness_id).first()
        if not weakness:
            raise ValueError(f"No weakness found with id {weakness_id}")
        
        # Update text and embedding
        embedding = self.embedding_model.embed_query(weakness_text)
        weakness.weakness_text = weakness_text
        weakness.embedding = embedding
        
        db.commit()
        db.refresh(weakness)
        return weakness.to_dict()
    
    def delete_weakness(self, db: Session, weakness_id: int) -> bool:
        """Delete a weakness."""
        weakness = db.query(UserWeakness).filter(UserWeakness.id == weakness_id).first()
        if weakness:
            db.delete(weakness)
            db.commit()
            return True
        return False

class TopicService:
    """Service for managing topics and their relationships with weaknesses."""
    
    def __init__(self):
        self.embedding_model = get_embeddings()
    
    def create_topic(self, db: Session, name: str, description: Optional[str] = None) -> Dict[str, Any]:
        """Create a new topic with vector embedding."""
        # Generate embedding from name and description
        text = f"{name}. {description}" if description else name
        embedding = self.embedding_model.embed_query(text)
        
        topic = Topic(
            name=name,
            description=description,
            embedding=embedding
        )
        db.add(topic)
        db.commit()
        db.refresh(topic)
        
        return {
            'id': topic.id,
            'name': topic.name,
            'description': topic.description
        }
    
    def link_weakness_to_topic(self, db: Session, topic_id: int, weakness_id: int, score: float) -> Dict[str, Any]:
        """Create or update topic-weakness relationship."""
        link = db.query(TopicWeakness)\
            .filter(TopicWeakness.topic_id == topic_id,
                   TopicWeakness.weakness_id == weakness_id)\
            .first()
        
        if link:
            link.relevance_score = score
        else:
            link = TopicWeakness(
                topic_id=topic_id,
                weakness_id=weakness_id,
                relevance_score=score
            )
            db.add(link)
        
        db.commit()
        db.refresh(link)
        
        return {
            'topic_id': link.topic_id,
            'weakness_id': link.weakness_id,
            'relevance_score': link.relevance_score
        }
    
    def get_topic_weaknesses(self, db: Session, topic_id: int) -> List[Dict[str, Any]]:
        """Get all weaknesses for a topic with relevance scores."""
        results = db.query(TopicWeakness, UserWeakness)\
            .join(UserWeakness)\
            .filter(TopicWeakness.topic_id == topic_id)\
            .order_by(TopicWeakness.relevance_score.desc())\
            .all()
        
        return [{
            **weakness.to_dict(),
            'relevance_score': link.relevance_score
        } for link, weakness in results]

# Create service instances
weakness_service = WeaknessService()
topic_service = TopicService()