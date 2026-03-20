from pydantic import BaseModel
from typing import Optional


class DebugRequest(BaseModel):
    error_trace: str
    session_id: Optional[str] = None


class DebugResponse(BaseModel):
    language: str
    error_type: str
    cause: str
    possible_fixes: list[str]
    confidence: float
