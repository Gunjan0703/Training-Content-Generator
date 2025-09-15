import os
from langchain_aws import ChatBedrockConverse

def bedrock_llm(model_id: str | None = None, temperature: float = 0.5, max_tokens: int = 2048):
    """
    Standard Bedrock LLM factory using Converse API.
    """
    return ChatBedrockConverse(
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        model_id=model_id or os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0"),
        model_kwargs={"temperature": temperature, "max_tokens": max_tokens}
    )
