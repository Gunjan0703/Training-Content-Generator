import os
from typing import TypedDict, Literal, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_aws import ChatBedrockConverse
from langchain_core.messages import HumanMessage, AIMessage

# State definition for the agent
class State(TypedDict):
    topic: str
    user_id: str
    user_role: str
    decision: Literal["pretest", "retrieve", "direct"]
    weaknesses: str
    draft: str
    errors: list[str]

def _llm(temp=0.3, max_tokens=1024):
    return ChatBedrockConverse(
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        model_id=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0"),
        model_kwargs={"temperature": temp, "max_tokens": max_tokens}
    )

def decide_path(state: State):
    """
    Decide best path:
      - 'retrieve': Use RAG to fetch weaknesses if the user has history
      - 'pretest': If topic is advanced and no history, create a quick pretest first
      - 'direct' : Go straight to generation if topic is basic or no infra
    """
    topic = state["topic"]
    role = state["user_role"]
    hint = (
        "Decide the best path for personalized module creation.\n"
        "Options:\n- retrieve: use RAG to fetch user weaknesses (if relevant)\n"
        "- pretest: create a 3-question quick pretest to assess gaps before the module\n"
        "- direct: directly generate module without extra steps\n"
        "Return only one word: retrieve, pretest, or direct."
    )
    msg = f"{hint}\n\nTopic: {topic}\nRole: {role}\n"
    text = (_llm(temp=0.2).invoke(msg).content or "").strip().lower()
    if "retrieve" in text:
        decision = "retrieve"
    elif "pretest" in text:
        decision = "pretest"
    else:
        decision = "direct"
    return {"decision": decision}

def maybe_retrieve_weaknesses(state: State):
    """
    Retrieve and summarize weaknesses from vector store if decision == 'retrieve'.
    Otherwise, keep weaknesses as empty string.
    """
    if state["decision"] != "retrieve":
        return {"weaknesses": ""}

    try:
        from app.services.rag_service import summarize_user_weaknesses
        wk = summarize_user_weaknesses(state["user_id"])
        return {"weaknesses": wk}
    except Exception as e:
        errs = list(state.get("errors", []))
        errs.append(f"retrieve:{e}")
        return {"weaknesses": "", "errors": errs}

def maybe_generate_pretest(state: State):
    """
    If decision == 'pretest', generate a short pretest (3 Qs, answer key).
    Append it as a top section to the final draft later.
    """
    if state["decision"] != "pretest":
        return {}

    prompt = (
        "Create a short pretest of 3 questions to quickly assess user knowledge on the topic below. "
        "Include an answer key.\n\n"
        f"Topic: {state['topic']}\nRole: {state['user_role']}"
    )
    try:
        pretest = _llm(temp=0.3, max_tokens=800).invoke(prompt).content
        return {"pretest": pretest}
    except Exception as e:
        errs = list(state.get("errors", []))
        errs.append(f"pretest:{e}")
        return {"pretest": "", "errors": errs}

def generate_draft(state: State):
    """
    Generate the personalized module. If weaknesses exist, include targeted remediation.
    If pretest exists (passed via state), prepend it.
    """
    wk = state.get("weaknesses", "")
    base = (
        f"You are a corporate training designer. Create a module on '{state['topic']}' "
        f"for role '{state['user_role']}'.\n"
        "Structure: introduction, 3-5 objectives, 2-4 sections with examples/exercises, and a summary.\n"
        "Tone: clear, practical, role-relevant.\n"
    )
    if wk:
        base += f"\nFocus remediation on these known weak areas: {wk}\n"

    draft = _llm(temp=0.6, max_tokens=2048).invoke(base).content
    # If pretest was generated earlier, attach it at the top
    pretest = state.get("pretest")
    if pretest:
        draft = f"## Pretest\n{pretest}\n\n## Module\n{draft}"
    return {"draft": draft}

def quality_check(state: State):
    """
    Light QC pass to ensure required sections exist.
    If missing, append a corrective addendum.
    """
    draft = state["draft"] or ""
    missing = []
    required = ["introduction", "objectives", "summary"]
    low = draft.lower()
    for sec in required:
        if sec not in low:
            missing.append(sec)
    if not missing:
        return {}
    addendum = _llm(temp=0.2, max_tokens=400).invoke(
        f"Add an addendum ensuring the draft includes or clarifies these missing sections: {', '.join(missing)}"
    ).content
    return {"draft": draft + "\n\n## Addendum\n" + addendum}

def build_graph():
    g = StateGraph(State)
    g.add_node("decide_path", decide_path)
    g.add_node("maybe_retrieve_weaknesses", maybe_retrieve_weaknesses)
    g.add_node("maybe_generate_pretest", maybe_generate_pretest)
    g.add_node("generate_draft", generate_draft)
    g.add_node("quality_check", quality_check)

    g.set_entry_point("decide_path")
    g.add_edge("decide_path", "maybe_retrieve_weaknesses")
    g.add_edge("maybe_retrieve_weaknesses", "maybe_generate_pretest")
    g.add_edge("maybe_generate_pretest", "generate_draft")
    g.add_edge("generate_draft", "quality_check")
    g.add_edge("quality_check", END)

    return g.compile()
