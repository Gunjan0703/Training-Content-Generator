import os
import json
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_aws import ChatBedrockConverse

class State(TypedDict):
    text: str
    target_language: str
    glossary: dict
    localize: bool
    style: str
    draft: str
    qa_notes: str
    final: str
    errors: list[str]

def _llm(temp=0.2, max_tokens=2048):
    return ChatBedrockConverse(
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        model_id=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0"),
        model_kwargs={"temperature": temp, "max_tokens": max_tokens}
    )

def translate(state: State):
    glossary_str = json.dumps(state.get("glossary", {}), ensure_ascii=False) if state.get("glossary") else ""
    glossary_note = f"Enforce glossary terms exactly: {glossary_str}" if glossary_str else ""
    loc_note = f"Adapt for {state['target_language']} locale (currencies, dates, idioms)." if state.get("localize") else ""
    style = state.get("style") or "neutral"

    prompt = (
        f"You are a professional translator.\n"
        f"Target language: {state['target_language']}\n"
        f"Style: {style}\n"
        f"{loc_note}\n{glossary_note}\n\n"
        f"Translate the following text. Respond with only the translation:\n---\n{state['text']}\n---"
    )
    draft = _llm().invoke(prompt).content
    return {"draft": draft}

def qa_check(state: State):
    """
    Perform a quick QA check: ensure glossary terms used, tone/style consistency,
    and that no untranslated fragments remain. Return notes and optionally a patch.
    """
    draft = state["draft"] or ""
    glossary = state.get("glossary") or {}
    checks = [
        "All required glossary terms present and correctly applied.",
        "No untranslated phrases or source-language artifacts remain.",
        "Style and tone match the requested style."
    ]
    qa_prompt = (
        "Quality-check the translation against these criteria:\n"
        f"- {checks}\n- {checks}\n- {checks[1]}\n\n"
        f"Glossary (if any): {json.dumps(glossary, ensure_ascii=False)}\n\n"
        "If issues exist, propose a corrected version; otherwise reply 'OK'.\n\n"
        f"Translation to check:\n---\n{draft}\n---"
    )
    notes = _llm(temp=0.1).invoke(qa_prompt).content
    if notes.strip().lower().startswith("ok"):
        return {"qa_notes": "OK"}
    # Apply patch heuristically: when the model returns a corrected version, prefer it
    # Simple heuristic: if notes contains a block with 'Corrected' or looks like a translation, use it
    corrected = notes
    return {"qa_notes": notes, "final": corrected}

def finalize(state: State):
    if state.get("final"):
        return {}
    return {"final": state["draft"]}

def build_graph():
    g = StateGraph(State)
    g.add_node("translate", translate)
    g.add_node("qa_check", qa_check)
    g.add_node("finalize", finalize)

    g.set_entry_point("translate")
    g.add_edge("translate", "qa_check")
    g.add_edge("qa_check", "finalize")
    g.add_edge("finalize", END)

    return g.compile()
