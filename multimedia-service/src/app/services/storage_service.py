from typing import Optional, Tuple
from sqlalchemy.orm import Session
from ..db import get_db
from .vector_db import MediaObject, Session

def save_media(filename: str, mimetype: str, data: bytes) -> int:
    """Save media file to database and return media_id."""
    size_bytes = len(data)
    
    for db in get_db():
        try:
            media = MediaObject(
                filename=filename,
                mimetype=mimetype,
                size_bytes=size_bytes,
                data=data
            )
            db.add(media)
            db.commit()
            db.refresh(media)
            return media.id
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to save media: {str(e)}")

def fetch_media(media_id: int) -> Optional[Tuple[str, str, int, bytes]]:
    """Fetch media file from database."""
    for db in get_db():
        media = db.query(MediaObject)\
            .filter(MediaObject.id == media_id)\
            .first()
        
        if media:
            return (
                media.filename,
                media.mimetype,
                media.size_bytes,
                media.data
            )
        return None
