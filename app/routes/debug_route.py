from fastapi import APIRouter
from app.schemas.debug_schema import DebugRequest, DebugResponse
from app.agent.graph import app_graph

router = APIRouter()


@router.post("/debug", response_model=DebugResponse)
def debug_error(request: DebugRequest):

    state = {
        "error": request.error_trace or ""
    }

    result = app_graph.invoke(state)

    parsed = result["parsed"]
    output = result["result"]

    return DebugResponse(
        language=parsed["language"],
        error_type=parsed["error_type"],
        cause=output["cause"],
        possible_fixes=output["fixes"],
        confidence=0.8,
        execution=result.get("execution")  # ⭐ NEW
    )
