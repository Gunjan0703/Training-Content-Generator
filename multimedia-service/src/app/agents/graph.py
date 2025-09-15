from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from .services.image_service import generate_and_store_image
from .services.analysis_service import summarize_transcript

class State(TypedDict):
    mode: Literal["image", "summarize"]
    prompt: str
    source_text: str
    media_id: int
    summary: str
    errors: list[str]

def decide(state: State):
    # If prompt is provided, assume image; if source_text provided, summarize
    if state.get("prompt"):
        return {"mode": "image"}
    if state.get("source_text"):
        return {"mode": "summarize"}
    return {"errors": state.get("errors", []) + ["decide: no input"]}

def do_image(state: State):
    try:
        mid = generate_and_store_image(state["prompt"])
        return {"media_id": mid}
    except Exception as e:
        return {"errors": state.get("errors", []) + [f"image:{e}"]}

def do_summarize(state: State):
    try:
        s = summarize_transcript(state["source_text"])
        return {"summary": s}
    except Exception as e:
        return {"errors": state.get("errors", []) + [f"summarize:{e}"]}

def build_graph():
    g = StateGraph(State)
    g.add_node("decide", decide)
    g.add_node("do_image", do_image)
    g.add_node("do_summarize", do_summarize)

    g.set_entry_point("decide")
    g.add_edge("decide", "do_image")
    g.add_edge("decide", "do_summarize")
    g.add_edge("do_image", END)
    g.add_edge("do_summarize", END)
    return g.compile()
