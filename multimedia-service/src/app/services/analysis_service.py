import os
from langchain_aws import ChatBedrockConverse
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

def _llm(temperature=0.3, max_tokens=1024):
    return ChatBedrockConverse(
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        model_id=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0"),
        model_kwargs={"temperature": temperature, "max_tokens": max_tokens}
    )

def summarize_transcript(text: str) -> str:
    tmpl = PromptTemplate(
        input_variables=["text"],
        template="Summarize this transcript into key points and action items:\n\n{text}"
    )
    chain = LLMChain(llm=_llm(), prompt=tmpl)
    return chain.invoke({"text": text})["text"]
