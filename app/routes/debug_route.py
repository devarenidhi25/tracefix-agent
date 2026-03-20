from fastapi import APIRouter
from app.schemas.debug_schema import DebugRequest, DebugResponse
from app.parsers.error_parser import parse_error

router = APIRouter()


@router.post("/debug", response_model=DebugResponse)
def debug_error(request: DebugRequest):
    parsed = parse_error(request.error_trace)

    return DebugResponse(
        language=parsed["language"],
        error_type=parsed["error_type"],
        cause="Basic parsing completed",
        possible_fixes=["Fix generation coming next"],
        confidence=0.3
    )
