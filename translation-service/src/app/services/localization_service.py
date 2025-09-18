import os
import json
import boto3
from botocore.config import Config

def get_bedrock_client():
    """Get a direct Bedrock client"""
    config = Config(region_name=os.getenv("AWS_REGION", "us-east-1"))
    return boto3.client('bedrock-runtime', config=config)

def localize_text(text: str, target_language: str, glossary: dict | None = None, localize: bool = False) -> str:
    """
    Translates and localizes a given text using direct Bedrock API.
    """
    client = get_bedrock_client()
    
    # Handle optional glossary and localization instructions
    glossary_data = glossary if glossary else {}
    localization_instruction_text = (
        "Adapt currencies, dates, idioms, and cultural references." if localize else ""
    )
    
    # Create the prompt
    prompt = (
        f"Translate the text into {target_language}.\n\n"
        f"Instructions: {localization_instruction_text}\n"
        f"Glossary: {glossary_data}\n\n"
        f"Text:\n---\n{text}\n---"
    )
    
    # Prepare the request body for Claude
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2048,
        "temperature": 0.2,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    try:
        # Make the API call
        response = client.invoke_model(
            modelId=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0"),
            body=json.dumps(body)
        )
        
        # Parse the response
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
        
    except Exception as e:
        raise Exception(f"Bedrock API call failed: {str(e)}")