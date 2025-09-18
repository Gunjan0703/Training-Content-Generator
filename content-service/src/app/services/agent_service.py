import os
from langchain_aws import ChatBedrockConverse

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

def _single_module(topic: str) -> str:
    prompt = (
        f"Create a comprehensive single-module training lesson on '{topic}' "
        f"with objectives, sections, and a summary."
    )
    return _llm().invoke(prompt).content

def create_full_curriculum(topic: str) -> dict:
    """
    Legacy path (non-LangGraph) for compatibility.
    Simple 2-step: ask for module titles, then draft each, then stitch.
    """
    # 1) list modules
    list_prompt = (
        f"List 3-6 course module titles for the topic '{topic}'. "
        f"Return ONLY a Python list of strings."
    )
    text = _llm(temperature=0.4, max_tokens=1024).invoke(list_prompt).content
    try:
        match = re.search(r"\[.*\]", text, re.S)
        modules = eval(match.group(0)) if match else [topic]
        if not isinstance(modules, list) or not modules:
            modules = [topic]
    except Exception:
        modules = [topic]

    # 2) draft each
    drafts = {}
    for m in modules:
        draft_prompt = (
            f"Create a detailed corporate training module for '{m}' "
            "with: intro, 3-5 objectives, 2-4 sections, and a summary."
        )
        try:
            drafts[m] = _llm().invoke(draft_prompt).content
        except Exception as e:
            drafts[m] = f"[ERROR generating '{m}']: {e}"

    # 3) combine
    join = "\n\n".join([f"### {k}\n{v}" for k, v in drafts.items()])
    combine_prompt = (
        f"Combine modules into a cohesive curriculum on '{topic}', avoid duplication, ensure clear flow.\n\n{join}"
    )
    try:
        curriculum = _llm(temperature=0.2).invoke(combine_prompt).content
    except Exception:
        curriculum = _single_module(topic)

    return {"plan": modules, "curriculum": curriculum}
