import psycopg2
from .db import get_conn

def save_media(filename: str, mimetype: str, data: bytes) -> int:
    sql = """
    INSERT INTO media_objects (filename, mimetype, size_bytes, data)
    VALUES (%s, %s, %s, %s) RETURNING id
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (filename, mimetype, len(data), psycopg2.Binary(data)))
        new_id = cur.fetchone()
        conn.commit()
        return new_id

def fetch_media(media_id: int):
    sql = "SELECT filename, mimetype, size_bytes, data FROM media_objects WHERE id=%s"
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, (media_id,))
        row = cur.fetchone()
        return row  # (filename, mimetype, size_bytes, data)
