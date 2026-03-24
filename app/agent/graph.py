from langgraph.graph import StateGraph, END

from app.parsers.error_parser import parse_error
from app.agent.reasoning_engine import generate_reasoning
from app.agent.llm_engine import llm_debug_analysis

from typing import TypedDict, Dict, Any, List


class DebugState(TypedDict, total=False):
    error: str
    parsed: Dict[str, Any]
    use_llm: bool
    result: Dict[str, Any]

    history: List[Dict[str, Any]]
    attempts: int
    done: bool


# 🔹 Node 1 — Parse
def parse_node(state: DebugState):
    error = state.get("error")

    if not error:
        raise ValueError(f"State missing 'error'. Current state: {state}")

    parsed = parse_error(error)

    return {
        **state,
        "parsed": parsed,
        "history": state.get("history", []),
        "attempts": state.get("attempts", 0)
    }


# 🔹 Node 2 — Decide
def decision_node(state: DebugState):
    parsed = state.get("parsed", {})
    attempts = state.get("attempts", 0)

    # First try → rule-based
    if attempts == 0:
        use_llm = parsed.get("error_type") == "Unknown"

    # Retry → always use LLM
    else:
        use_llm = True

    return {
        **state,
        "use_llm": use_llm
    }


# 🔹 Node 3 — Reason
def reasoning_node(state: DebugState):
    parsed = state.get("parsed", {})
    use_llm = state.get("use_llm", False)
    error = state.get("error", "")
    history = state.get("history", [])

    # Build context
    context = ""
    for step in history:
        context += f"""
Previous Error: {step.get('error')}
Cause: {step.get('cause')}
Fixes Tried: {step.get('fixes')}
"""

    if use_llm:
        result = llm_debug_analysis(context, error)
    else:
        result = generate_reasoning(parsed)

    # Update history
    new_history = history + [{
        "error": error,
        "cause": result["cause"],
        "fixes": result["fixes"]
    }]

    return {
        **state,
        "result": result,
        "history": new_history,
        "attempts": state.get("attempts", 0) + 1
    }


def check_node(state: DebugState):
    attempts = state.get("attempts", 0)

    done = attempts >= 2

    return {
        **state,
        "done": done
    }


# 🔹 Build Graph
graph = StateGraph(DebugState)

graph.add_node("parse", parse_node)
graph.add_node("decide", decision_node)
graph.add_node("reason", reasoning_node)
graph.add_node("check", check_node)

graph.set_entry_point("parse")

graph.add_edge("parse", "decide")
graph.add_edge("decide", "reason")
graph.add_edge("reason", "check")


# 🔥 CONDITIONAL LOOP
def should_continue(state: DebugState):
    return "decide" if not state.get("done") else END


graph.add_conditional_edges("check", should_continue)

app_graph = graph.compile()
