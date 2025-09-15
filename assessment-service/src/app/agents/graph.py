import os
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_aws import ChatBedrockConverse

def _llm(temperature=0.4, max_tokens=2048):
    return ChatBedrockConverse(
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        model_id=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0"),
        model_kwargs={"temperature": temperature, "max_tokens": max_tokens}
    )

def _chain(template: str):
    prompt = PromptTemplate(input_variables=["content"], template=template)
    return LLMChain(llm=_llm(), prompt=prompt)

TEMPLATES = {
    "multiple_choice": """You are an expert quiz designer. Based on the content below, create a 5-question multiple-choice quiz.
- Each question must have 4 options (A, B, C, D).
- Only one option is correct; clearly mark the correct choice in an answer key at the end.

Content:
---
{content}
---
""",
    "scenario": """You are an instructional designer. Based on the content below, create one realistic workplace scenario that tests practical decision-making.
- Provide a detailed scenario and a single clear question about the best next action.
- Provide an 'Ideal Answer' with justification referencing the content.

Content:
---
{content}
---
""",
    "fill_in_the_blanks": """You are a meticulous editor. From the content below, create 5 fill-in-the-blanks items.
- Each item is a complete sentence with a single blank '____'.
- Provide an answer key at the end.

Content:
---
{content}
---
"""
}

def create_advanced_assessment(content: str, assessment_type: str) -> str:
    template = TEMPLATES.get(assessment_type, TEMPLATES["multiple_choice"])
    chain = _chain(template)
    resp = chain.invoke({"content": content})
    return resp["text"]
