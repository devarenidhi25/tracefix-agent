from langgraph.graph import StateGraph, END

from app.parsers.error_parser import parse_error
from app.agent.reasoning_engine import generate_reasoning
from app.agent.llm_engine import llm_debug_analysis

from typing import TypedDict, Dict, Any


# 🧠 Define state structure
class DebugState(TypedDict, total=False):
    error: str
    parsed: Dict[str, Any]
    use_llm: bool
    result: Dict[str, Any]


# 🔹 Node 1 — Parse
def parse_node(state: DebugState):
    error = state.get("error")

    if not error:
        raise ValueError(f"State missing 'error'. Current state: {state}")

    parsed = parse_error(error)

    return {
        **state,
        "parsed": parsed
    }


# 🔹 Node 2 — Decide
def decision_node(state: DebugState):
    parsed = state.get("parsed", {})

    use_llm = parsed.get("error_type") == "Unknown"

    return {
        **state,
        "use_llm": use_llm
    }


# 🔹 Node 3 — Reason
def reasoning_node(state: DebugState):
    parsed = state.get("parsed", {})
    use_llm = state.get("use_llm", False)
    error = state.get("error", "")

    if use_llm:
        result = llm_debug_analysis("", error)
    else:
        result = generate_reasoning(parsed)

    return {
        **state,
        "result": result
    }


# 🔹 Build Graph
graph = StateGraph(DebugState)

graph.add_node("parse", parse_node)
graph.add_node("decide", decision_node)
graph.add_node("reason", reasoning_node)

graph.set_entry_point("parse")

graph.add_edge("parse", "decide")
graph.add_edge("decide", "reason")
graph.add_edge("reason", END)   # ⭐ IMPORTANT

app_graph = graph.compile()
