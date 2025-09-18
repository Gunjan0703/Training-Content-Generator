import os
from typing import TypedDict
from langgraph.graph import StateGraph
from langchain_aws import ChatBedrockConverse
from .tools import difficulty_estimator

class State(TypedDict):
    content: str
    choice: str
    output: str

def _model():
    return ChatBedrockConverse(
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        model_id=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0"),
        model_kwargs={"temperature": 0.2}
    )

def choose_type(state: State):
    """
    Use LLM + heuristic to select assessment type.
    """
    content = state["content"]
    diff = difficulty_estimator(content).get("difficulty", "intermediate")

    # Prompt hint to the LLM; it can override heuristic if it finds scenarios/coding clues
    hint = f"Difficulty={diff}. Choose the best assessment type: multiple_choice, scenario, or fill_in_the_blanks. Respond with only the type."
    resp = _model().invoke(f"{hint}\n\nCONTENT:\n{content[:4000]}")
    text = (resp.content or "").strip().lower()

    if "scenario" in text:
        choice = "scenario"
    elif "fill" in text:
        choice = "fill_in_the_blanks"
    elif "multiple" in text or "choice" in text:
        choice = "multiple_choice"
    else:
        # fallback to heuristic
        choice = "multiple_choice" if diff in {"beginner", "intermediate"} else "scenario"

    return {"choice": choice}

def generate(state: State):
    """
    Generate assessment using the legacy generator_service for the chosen type.
    """
    from app.services.generator_service import create_advanced_assessment
    output = create_advanced_assessment(state["content"], state["choice"])
    return {"output": output}

def build_graph():
    g = StateGraph(State)
    g.add_node("choose_type", choose_type)
    g.add_node("generate", generate)
    g.set_entry_point("choose_type")
    g.add_edge("choose_type", "generate")
    return g.compile()
