import os
from langchain_aws import ChatBedrockConverse
from typing import List, Dict

def _llm(temperature=0.7, max_tokens=2048, model_id: str = None):
    model = model_id or os.getenv(
        "BEDROCK_MODEL_ID",
        "anthropic.claude-3-haiku-20240307-v1:0"
    )
    return ChatBedrockConverse(
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        model_id=model,
        temperature=temperature,
        max_tokens=max_tokens
    )

def topic_deconstructor(topic: str) -> List[str]:
    """
    Ask the LLM to output only a Python list of strings (module titles).
    """
    prompt = (
        f"You are an expert curriculum planner. "
        f"Break down the topic '{topic}' into 3-6 course module titles. "
        f"Return ONLY a Python list of strings like ['Intro', 'Module 2', ...]."
    )
    text = _llm(temperature=0.4).invoke(prompt).content
    match = re.search(r"\[.*\]", text, re.S)
    if not match:
        return [topic]
    try:
        modules = eval(match.group(0))
        if isinstance(modules, list) and all(isinstance(m, str) for m in modules):
            return modules
    except Exception:
        pass
    return [topic]

def module_generator(title: str) -> str:
    """
    Generate a comprehensive module with:
    - Intro
    - 3-5 Learning Objectives
    - 2-4 Sections with examples
    - Summary
    """
    prompt = (
        "You are an instructional designer. "
        f"Create a detailed training module for '{title}' with:\n"
        "1) An engaging introduction\n"
        "2) 3-5 learning objectives\n"
        "3) 2-4 main sections with concrete examples and bullets\n"
        "4) A concise summary\n"
        "Keep it clear, structured, and suitable for corporate training."
    )
    return _llm(temperature=0.6, max_tokens=4096).invoke(prompt).content

def combine_modules(topic: str, modules: Dict[str, str]) -> str:
    """
    Combine generated modules into a coherent curriculum, remove duplication, ensure flow.
    """
    joined = "\n\n".join([f"### {k}\n{v}" for k, v in modules.items()])
    prompt = (
        f"Combine the following modules into a cohesive curriculum on '{topic}'. "
        "Ensure smooth progression, avoid duplication, and add transitional notes between modules where helpful.\n\n"
        f"{joined}"
    )
    return _llm(temperature=0.2, max_tokens=4096).invoke(prompt).content
