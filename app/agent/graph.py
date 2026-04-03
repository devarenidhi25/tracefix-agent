from langgraph.graph import StateGraph, END
from typing import TypedDict, Dict, Any, List, Annotated

from app.parsers.error_parser import parse_error
from app.agent.reasoning_engine import generate_reasoning
from app.agent.llm_engine import llm_debug_analysis
from app.tools.code_editor import apply_import_fix


def error_reducer(left: str, right: str) -> str:
    return right if right else left


class DebugState(TypedDict, total=False):
    error: Annotated[str, error_reducer]
    parsed: Dict[str, Any]
    use_llm: bool
    result: Dict[str, Any]

    history: List[Dict[str, Any]]
    attempts: int
    done: bool
    execution: Dict[str, Any]


# 🔹 Node 1 — Parse
def parse_node(state: DebugState):
    error = state.get("error")

    if not error:
        raise ValueError("Missing error")

    return {
        "parsed": parse_error(error),
        "history": state.get("history", []),
        "attempts": state.get("attempts", 0)
    }


# 🔹 Node 2 — Decide
def decision_node(state: DebugState):
    parsed = state["parsed"]
    attempts = state["attempts"]

    if attempts == 0:
        use_llm = parsed["error_type"] == "Unknown"
    else:
        use_llm = True

    return {
        "use_llm": use_llm
    }


# 🔹 Node 3 — Reason
def reasoning_node(state: DebugState):
    parsed = state["parsed"]
    use_llm = state["use_llm"]
    error = state["error"]
    history = state.get("history", [])

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

    new_history = history + [{
        "error": error,
        "cause": result["cause"],
        "fixes": result["fixes"]
    }]

    return {
        "result": result,
        "history": new_history,
        "attempts": state["attempts"] + 1
    }


# 🔹 Node 4 — Execute
def execute_fix_node(state: DebugState):
    parsed = state["parsed"]
    error_type = parsed.get("error_type")

    file_path = "test.py"

    execution_result = {"status": "no_action"}

    if error_type == "Missing Dependency":
        execution_result = {
            "status": "simulated",
            "message": "Would run pip install python-dotenv"
        }

    elif error_type == "Import Error":
        execution_result = apply_import_fix(
            file_path,
            "from dotenv import load_dotenv"
        )

    return {
        "execution": execution_result
    }


# 🔹 Node 5 — Check
def check_node(state: DebugState):
    attempts = state["attempts"]
    done = attempts >= 2

    return {
        "done": done
    }


# 🔹 Graph
graph = StateGraph(DebugState)

graph.add_node("parse", parse_node)
graph.add_node("decide", decision_node)
graph.add_node("reason", reasoning_node)
graph.add_node("execute", execute_fix_node)
graph.add_node("check", check_node)

graph.set_entry_point("parse")

graph.add_edge("parse", "decide")
graph.add_edge("decide", "reason")
graph.add_edge("reason", "execute")
graph.add_edge("execute", "check")


def should_continue(state: DebugState):
    return "decide" if not state.get("done") else END


graph.add_conditional_edges("check", should_continue)

app_graph = graph.compile()