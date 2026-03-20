from fastapi import APIRouter
from app.schemas.debug_schema import DebugRequest, DebugResponse
from app.parsers.error_parser import parse_error
from app.agent.reasoning_engine import generate_reasoning

router = APIRouter()


@router.post("/debug", response_model=DebugResponse)
def debug_error(request: DebugRequest):
    parsed = parse_error(request.error_trace)
    reasoning = generate_reasoning(parsed)

    return DebugResponse(
        language=parsed["language"],
        error_type=parsed["error_type"],
        cause=reasoning["cause"],
        possible_fixes=reasoning["fixes"],
        confidence=0.6
    )
