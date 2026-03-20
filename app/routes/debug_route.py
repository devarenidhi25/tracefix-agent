from fastapi import APIRouter
from app.schemas.debug_schema import DebugRequest, DebugResponse

router = APIRouter()


@router.post("/debug", response_model=DebugResponse)
def debug_error(request: DebugRequest):
    # temporary dummy response
    return DebugResponse(
        language="Python",
        error_type="Unknown",
        cause="This is a placeholder response",
        possible_fixes=["Fix will be generated soon"],
        confidence=0.0
    )
