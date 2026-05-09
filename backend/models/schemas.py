from pydantic import BaseModel
from typing import Optional


class PipelineStatus(BaseModel):
    agent_id: str
    status: str  # idle / running / done / error
    result: dict | None = None
    error: str | None = None


class PipelineResponse(BaseModel):
    session_id: str
    events: list[PipelineStatus]


class GenerateImageRequest(BaseModel):
    positive_prompt: str
