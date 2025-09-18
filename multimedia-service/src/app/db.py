import os
import psycopg2

def get_conn():
    return psycopg2.connect(
        dbname=os.getenv("PGDATABASE", "training"),
        user=os.getenv("PGUSER", "training"),
        password=os.getenv("PGPASSWORD", "training"),
        host=os.getenv("PGHOST", "postgres"),
        port=int(os.getenv("PGPORT", "5432")),
    )

def init_schema():
    create_media = """
    CREATE TABLE IF NOT EXISTS media_objects (
      id SERIAL PRIMARY KEY,
      filename TEXT NOT NULL,
      mimetype TEXT NOT NULL,
      size_bytes BIGINT NOT NULL,
      data BYTEA NOT NULL,
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(create_media)
        conn.commit()
