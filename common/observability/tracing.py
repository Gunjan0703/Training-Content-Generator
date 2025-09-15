import os

def init_tracing():
    """
    Initialize Langfuse tracing if keys are provided.
    Safe no-op when not configured.
    """
    public = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret = os.getenv("LANGFUSE_SECRET_KEY")
    host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

    if not (public and secret):
        return None

    try:
        from langfuse import Langfuse
        client = Langfuse(public_key=public, secret_key=secret, host=host)
        # Optionally return client or set up global callbacks for LangChain/LangGraph
        return client
    except Exception:
        # Do not crash service if tracing backend is unavailable
        return None
