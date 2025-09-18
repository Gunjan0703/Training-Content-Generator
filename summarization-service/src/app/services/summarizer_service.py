import os
from langchain_aws import ChatBedrockConverse
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

def _llm(temperature=0.3, max_tokens=2048):
    """
    Use Bedrock Converse via LangChain for robust summarization.
    Pass temperature and max_tokens directly (not via model_kwargs)
    """
    return ChatBedrockConverse(
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        model_id=os.getenv(
            "BEDROCK_MODEL_ID",
            "anthropic.claude-3-5-sonnet-20240620-v1:0"
        ),
        temperature=temperature,  # <- pass directly
        max_tokens=max_tokens      # <- pass directly
        # remove model_kwargs entirely
    )

def summarize_text_custom(text: str, format_type: str, length: str) -> str:
    """
    Summarize text with user-controlled format and length.
    length in {"short","medium","long"}
    format_type examples: "bulleted list", "paragraph"
    """
    length_map = {
        "short": "one concise paragraph",
        "medium": "a bulleted list of 3-5 key points",
        "long": "a detailed summary with an introduction, key findings, and a conclusion"
    }
    desc = length_map.get(length, length_map["medium"])

    template = (
        "You are a professional summarizer.\n\n"
        "Summarize the input text into a {format_type} with {desc}.\n\n"
        "Text:\n---\n{text}\n---\n"
        "Respond with only the summary."
    )
    prompt = PromptTemplate(
        input_variables=["text", "format_type", "desc"],
        template=template
    )
    chain = LLMChain(llm=_llm(), prompt=prompt)
    resp = chain.invoke({"text": text, "format_type": format_type, "desc": desc})
    return resp["text"]
