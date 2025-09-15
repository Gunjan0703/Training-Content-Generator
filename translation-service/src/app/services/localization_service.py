import os
import json
from langchain_aws import ChatBedrockConverse
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

def _llm(temperature=0.2, max_tokens=2048):
    return ChatBedrockConverse(
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        model_id=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0"),
        model_kwargs={"temperature": temperature, "max_tokens": max_tokens}
    )

def localize_text(text: str, target_language: str, glossary: dict | None = None, localize: bool = False) -> str:
    glossary_instructions = ""
    if glossary:
        glossary_json = json.dumps(glossary, ensure_ascii=False)
        glossary_instructions = (
            f"CRITICAL: Enforce the following term translations exactly as approved: {glossary_json}"
        )

    localization_instructions = ""
    if localize:
        localization_instructions = (
            f"This is a localization task for {target_language} audiences. Adapt currencies, dates, idioms, and cultural references."
        )

    template = (
        "Translate the text into {target_language}.\n\n"
        "{localization_instructions}\n"
        "{glossary_instructions}\n\n"
        "Text:\n---\n{text}\n---\n\n"
        "Provide only the translated/localized text, with no commentary."
    )

    prompt = PromptTemplate(
        input_variables=["text", "target_language", "localization_instructions", "glossary_instructions"],
        template=template
    )
    chain = LLMChain(llm=_llm(), prompt=prompt)
    resp = chain.invoke({
        "text": text,
        "target_language": target_language,
        "localization_instructions": localization_instructions,
        "glossary_instructions": glossary_instructions
    })
    return resp["text"]
