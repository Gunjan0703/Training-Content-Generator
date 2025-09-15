import os
from typing import Optional
from langchain_aws import BedrockEmbeddings
from langchain_community.vectorstores import OpenSearchVectorSearch

def embeddings():
    """
    Amazon Titan Text Embeddings for vectorization.
    """
    return BedrockEmbeddings(
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        model_id=os.getenv("BEDROCK_EMBED_MODEL_ID", "amazon.titan-embed-text-v2:0")
    )

def get_store() -> OpenSearchVectorSearch:
    """
    Connect to OpenSearch vector index for user weaknesses.
    Required env:
      OPENSEARCH_HOST, OPENSEARCH_INDEX, OPENSEARCH_USER, OPENSEARCH_PASS
    """
    host = os.getenv("OPENSEARCH_HOST")
    index = os.getenv("OPENSEARCH_INDEX", "user-weakness")
    user = os.getenv("OPENSEARCH_USER")
    pwd = os.getenv("OPENSEARCH_PASS")

    if not host:
        raise RuntimeError("OPENSEARCH_HOST is not configured")

    return OpenSearchVectorSearch(
        index_name=index,
        embedding_function=embeddings(),
        opensearch_url=host,
        http_auth=(user, pwd) if user and pwd else None,
    )
