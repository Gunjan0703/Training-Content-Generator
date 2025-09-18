from .db import get_conn

def init_transcript_schema():
    sql = """
    CREATE TABLE IF NOT EXISTS transcripts (
      id SERIAL PRIMARY KEY,
      source_uri TEXT NOT NULL,
      text TEXT NOT NULL,
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql)
        conn.commit()

def save_transcript(source_uri: str, text: str) -> int:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO transcripts(source_uri, text) VALUES (%s,%s) RETURNING id",
            (source_uri, text),
        )
        new_id = cur.fetchone()
        conn.commit()
        return new_id

def fetch_transcript(tid: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT source_uri, text FROM transcripts WHERE id=%s", (tid,))
        return cur.fetchone()
