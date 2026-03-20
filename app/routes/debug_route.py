from fastapi import APIRouter
from app.schemas.debug_schema import DebugRequest, DebugResponse
from app.parsers.error_parser import parse_error
from app.agent.reasoning_engine import generate_reasoning
from app.agent.llm_engine import llm_debug_analysis
router = APIRouter()


@router.post("/debug", response_model=DebugResponse)
def debug_error(request: DebugRequest):
    parsed = parse_error(request.error_trace)
    reasoning = generate_reasoning(parsed)

    # Decision: when to use LLM
    if parsed["error_type"] == "Unknown":
        llm_result = llm_debug_analysis(request.error_trace)

        cause = llm_result["cause"]
        fixes = llm_result["fixes"]
        confidence = 0.8
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
