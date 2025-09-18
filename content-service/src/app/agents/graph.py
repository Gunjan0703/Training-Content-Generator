from typing import Dict, List, TypedDict
from langgraph.graph import StateGraph
from .tools import topic_deconstructor, module_generator, combine_modules

class State(TypedDict):
    topic: str
    modules: List[str]
    drafts: Dict[str, str]
    final: str
    errors: List[str]

def plan(state: State):
    try:
        modules = topic_deconstructor(state["topic"])
        return {"modules": modules}
    except Exception as e:
        return {"errors": state.get("errors", []) + [f"plan:{e}"]}

def write_each(state: State):
    drafts = dict(state.get("drafts", {}))
    for title in state["modules"]:
        if title not in drafts or not drafts[title]:
            try:
                drafts[title] = module_generator(title)
            except Exception as e:
                drafts[title] = f"[ERROR generating '{title}']: {e}"
    return {"drafts": drafts}

def assemble(state: State):
    try:
        final_text = combine_modules(state["topic"], state["drafts"])
        return {"final": final_text}
    except Exception as e:
        return {"errors": state.get("errors", []) + [f"assemble:{e}"]}

def build_graph():
    g = StateGraph(State)
    g.add_node("plan", plan)
    g.add_node("write_each", write_each)
    g.add_node("assemble", assemble)
    g.set_entry_point("plan")
    g.add_edge("plan", "write_each")
    g.add_edge("write_each", "assemble")
    return g.compile()
