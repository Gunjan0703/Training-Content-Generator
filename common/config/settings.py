import os

class Settings:
    # Environment
    ENV: str = os.getenv("ENV", "dev")

    # AWS / Bedrock
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    BEDROCK_MODEL_ID: str = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0")
    BEDROCK_EMBED_MODEL_ID: str = os.getenv("BEDROCK_EMBED_MODEL_ID", "amazon.titan-embed-text-v2:0")

    # OpenSearch (for personalization RAG)
    OPENSEARCH_HOST: str | None = os.getenv("OPENSEARCH_HOST")
    OPENSEARCH_INDEX: str = os.getenv("OPENSEARCH_INDEX", "user-weakness")
    OPENSEARCH_USER: str | None = os.getenv("OPENSEARCH_USER")
    OPENSEARCH_PASS: str | None = os.getenv("OPENSEARCH_PASS")

    # PostgreSQL (local DB for multimedia)
    PGHOST: str = os.getenv("PGHOST", "postgres")
    PGPORT: int = int(os.getenv("PGPORT", "5432"))
    PGDATABASE: str = os.getenv("PGDATABASE", "training")
    PGUSER: str = os.getenv("PGUSER", "training")
    PGPASSWORD: str = os.getenv("PGPASSWORD", "training")

    # Feature flags
    ENABLE_AGENTS: bool = os.getenv("ENABLE_AGENTS", "true").lower() == "true"

    # Observability (Langfuse optional)
    LANGFUSE_PUBLIC_KEY: str | None = os.getenv("LANGFUSE_PUBLIC_KEY")
    LANGFUSE_SECRET_KEY: str | None = os.getenv("LANGFUSE_SECRET_KEY")
    LANGFUSE_HOST: str = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

settings = Settings()
