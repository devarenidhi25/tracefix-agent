from fastapi import APIRouter
from app.schemas.debug_schema import DebugRequest, DebugResponse
from app.parsers.error_parser import parse_error
from app.agent.reasoning_engine import generate_reasoning
from app.agent.llm_engine import llm_debug_analysis
from app.memory.session_store import get_session, add_to_session
router = APIRouter()


@router.post("/debug", response_model=DebugResponse)
def debug_error(request: DebugRequest):
    parsed = parse_error(request.error_trace)

    # 🧠 MEMORY LOGIC
    history = []
    if request.session_id:
        history = get_session(request.session_id)
        add_to_session(request.session_id, request.error_trace)

    reasoning = generate_reasoning(parsed)

    # 🤖 DECISION LOGIC (UPDATED)
    use_llm = False

    if parsed["error_type"] == "Unknown":
        use_llm = True

    # ⭐ NEW: if session has history → use LLM
    if history:
        use_llm = True

    if use_llm:
        llm_result = llm_debug_analysis(
            history,
            request.error_trace
        )
        cause = llm_result["cause"]
        fixes = llm_result["fixes"]
        confidence = 0.85
    else:
        cause = reasoning["cause"]
        fixes = reasoning["fixes"]
        confidence = 0.6

    return DebugResponse(
        language=parsed["language"],
        error_type=parsed["error_type"],
        cause=cause,
        possible_fixes=fixes,
        confidence=confidence
    )
