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

    # 🧠 MEMORY FETCH
    history = []
    if request.session_id:
        history = get_session(request.session_id)

    reasoning = generate_reasoning(parsed)

    # 🤖 DECISION LOGIC (FINAL FIXED ORDER)
    use_llm = False

    # 1. If unknown → use LLM
    if parsed["error_type"] == "Unknown":
        use_llm = True

    # 2. If repeated error → use LLM (strong signal)
    if history:
        last_error = history[-1]["error"]
        if last_error == request.error_trace:
            use_llm = True

    # 3. Known errors → force rule-based (override)
    if parsed["error_type"] in ["Missing Dependency", "Import Error", "Syntax Error"]:
        use_llm = False

    # 🧠 BUILD CONTEXT TEXT
    context_text = ""
    if history:
        for step in history:
            context_text += f"""
Previous Error: {step.get('error')}
Cause: {step.get('cause')}
Fixes Tried: {step.get('fixes')}
"""

    # 🧠 COLLECT PREVIOUS FIXES
    previous_fixes = []
    if history:
        for step in history:
            previous_fixes.extend(step.get("fixes", []))

    # 🤖 LLM OR RULE
    if use_llm:
        llm_result = llm_debug_analysis(
            f"""
{context_text}

Avoid repeating these fixes:
{previous_fixes}
""",
            request.error_trace
        )
        cause = llm_result["cause"]
        fixes = llm_result["fixes"]
        confidence = 0.85

        # 🧠 GUARDRAIL (CRITICAL)
        # fallback if LLM gives nonsense for known errors
        if parsed["error_type"] == "Missing Dependency":
            # Always trust rule-based for this type
            cause = reasoning["cause"]
            fixes = reasoning["fixes"]
            confidence = 0.6

    else:
        cause = reasoning["cause"]
        fixes = reasoning["fixes"]
        confidence = 0.6

    # 🧠 STORE AFTER PROCESSING
    if request.session_id:
        add_to_session(
            request.session_id,
            {
                "error": request.error_trace,
                "cause": cause,
                "fixes": fixes
            }
        )

    return DebugResponse(
        language=parsed["language"],
        error_type=parsed["error_type"],
        cause=cause,
        possible_fixes=fixes,
        confidence=confidence
    )
