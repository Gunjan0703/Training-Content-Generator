import os
from typing import Optional
from langchain_aws import BedrockEmbeddings
from langchain_community.vectorstores import PGVector

def embeddings():
    return BedrockEmbeddings(
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        model_id=os.getenv("BEDROCK_EMBED_MODEL_ID", "amazon.titan-embed-text-v2:0"),
    )

def get_store(collection_name: Optional[str] = None) -> PGVector:
    """
    Connect to Postgres pgvector for user weaknesses.
    Env:
      DATABASE_URL=postgresql+psycopg://user:pass@host:port/dbname
      PGVECTOR_COLLECTION=user_weakness
    Requires:
      CREATE EXTENSION IF NOT EXISTS vector;  (run once in shared init)
    """
    conn = os.getenv("DATABASE_URL")
    if not conn:
        raise RuntimeError("DATABASE_URL is not configured")
    coll = collection_name or os.getenv("PGVECTOR_COLLECTION", "user_weakness")
    return PGVector(
        connection_string=conn,
        collection_name=coll,
        embedding_function=embeddings(),
    )
