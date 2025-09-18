import os
from typing import TypedDict, Literal, Annotated
from langgraph.graph import StateGraph, END
from langchain_aws import ChatBedrockConverse
import json
from app.services.vector_store_pg import get_user_weaknesses

class State(TypedDict):
    topic: str
    user_id: str
    user_role: str
    decision: Literal["pretest", "retrieve", "direct"]
    weaknesses: str
    draft: str
    errors: list[str]
    pretest: str

def _llm(temp=0.3, max_tokens=1024):
    """Initialize AWS Bedrock Claude model with given parameters."""
    return ChatBedrockConverse(
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        model_id=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0"),
        temperature=temp,
        max_tokens=max_tokens
    )

def decide_path(state: State) -> dict:
    """
    Decide the best path for content personalization based on topic and role.
    Returns: Updated state with decision key.
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
    text = (_llm(temp=0.2).invoke(f"{hint}\n\nTopic: {topic}\nRole: {role}").content or "").strip().lower()
    if "retrieve" in text:
        decision = "retrieve"
    elif "pretest" in text:
        decision = "pretest"
    else:
        decision = "direct"
    return {"decision": decision}

def maybe_retrieve_weaknesses(state: State) -> dict:
    """
    Optionally retrieve user weaknesses if decision is 'retrieve'.
    Returns: Updated state with weaknesses and any errors.
    """
    if state["decision"] != "retrieve":
        return {"weaknesses": ""}
    try:
        weaknesses = get_user_weaknesses(state["user_id"])
        if not weaknesses:
            return {"weaknesses": ""}
        
        # Summarize weaknesses into a coherent text
        weakness_texts = [w["weakness_text"] for w in weaknesses]
        prompt = f"Summarize these learning gaps into 2-3 key areas:\n{json.dumps(weakness_texts)}"
        summary = _llm(temp=0.2).invoke(prompt).content
        
        return {"weaknesses": summary}
    except Exception as e:
        errs = list(state.get("errors", []))
        errs.append(f"retrieve:{e}")
        return {"weaknesses": "", "errors": errs}

def maybe_generate_pretest(state: State) -> dict:
    """
    Optionally generate a pretest if decision is 'pretest'.
    Returns: Updated state with pretest content and any errors.
    """
    if state["decision"] != "pretest":
        return {}
    prompt = (
        "Create a short pretest of 3 questions to quickly assess user knowledge on the topic below. "
        "Format:\n1. Multiple choice questions labeled Q1-Q3\n"
        "2. Clear answer key with explanations\n"
        "3. Focus on key concepts and common misconceptions\n\n"
        f"Topic: {state['topic']}\nRole: {state['user_role']}"
    )
    try:
        pretest = _llm(temp=0.3, max_tokens=800).invoke(prompt).content
        return {"pretest": str(pretest)}
    except Exception as e:
        errs = list(state.get("errors", []))
        errs.append(f"pretest:{e}")
        return {"pretest": "", "errors": errs}

def generate_draft(state: State) -> dict:
    """
    Generate personalized training content based on state context.
    Returns: Updated state with draft content.
    """
    wk = state.get("weaknesses", "")
    base = (
        f"You are a corporate training designer. Create a module on '{state['topic']}' "
        f"for role '{state['user_role']}'.\n"
        "Required Structure:\n"
        "1. Introduction (context and relevance)\n"
        "2. Learning Objectives (3-5 clear, measurable objectives)\n"
        "3. Main Content (2-4 sections with practical examples)\n"
        "4. Exercises (hands-on practice activities)\n"
        "5. Summary (key takeaways)\n\n"
        "Style Guide:\n"
        "- Clear, concise language\n"
        "- Role-specific examples\n"
        "- Practical applications\n"
        "- Progressive complexity\n"
    )
    if wk:
        base += f"\nFocus on addressing these identified gaps:\n{wk}\n"

    try:
        draft = _llm(temp=0.6, max_tokens=2048).invoke(base).content
        pretest = state.get("pretest")
        if pretest:
            draft = f"## Pretest\n{pretest}\n\n## Training Module\n{draft}"
        return {"draft": str(draft)}
    except Exception as e:
        errs = list(state.get("errors", []))
        errs.append(f"draft:{e}")
        return {"draft": "", "errors": errs}

def quality_check(state: State) -> dict:
    """
    Verify content meets quality standards and add missing sections.
    Returns: Updated state with improved content if needed.
    """
    draft = state["draft"] or ""
    missing = []
    required = ["introduction", "objectives", "summary", "exercises"]
    low = draft.lower()
    
    for sec in required:
        if sec not in low:
            missing.append(sec)
            
    if not missing:
        return {}
        
    try:
        prompt = (
            f"Add these missing sections to the training module: {', '.join(missing)}.\n"
            "Keep the additions concise but meaningful, matching the existing style and flow.\n"
            "Original content:\n\n{draft}"
        )
        improved = _llm(temp=0.2, max_tokens=1024).invoke(prompt).content
        return {"draft": improved}
    except Exception as e:
        errs = list(state.get("errors", []))
        errs.append(f"quality:{e}")
        return {"errors": errs}

def build_graph() -> StateGraph:
    """
    Build the LangGraph workflow for content personalization.
    Returns: Configured StateGraph ready for execution.
    """
    # Create the graph
    workflow = StateGraph(State)
    
    # Add nodes
    workflow.add_node("decide_path", decide_path)
    workflow.add_node("retrieve_weaknesses", maybe_retrieve_weaknesses)
    workflow.add_node("generate_pretest", maybe_generate_pretest)
    workflow.add_node("generate_draft", generate_draft)
    workflow.add_node("quality_check", quality_check)
    
    # Configure edges
    workflow.set_entry_point("decide_path")
    workflow.add_edge("decide_path", "retrieve_weaknesses")
    workflow.add_edge("retrieve_weaknesses", "generate_pretest")
    workflow.add_edge("generate_pretest", "generate_draft")
    workflow.add_edge("generate_draft", "quality_check")
    workflow.add_edge("quality_check", END)
    
    # Compile
    return workflow.compile()
    return {"draft": draft + "\n\n## Addendum\n" + str(addendum)}  # ensure string

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
