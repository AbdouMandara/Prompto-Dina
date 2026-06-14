from typing import List, Optional

from pydantic import BaseModel, Field


class PromptRequest(BaseModel):
    idea: str = Field(..., max_length=2000, min_length=1)
    objective: str = Field(..., max_length=500)
    role: str = Field(..., max_length=200)
    level: str = Field(..., max_length=100)
    responseFormat: str = Field(..., max_length=200)
    tone: str = Field(..., max_length=100)
    length: str = Field(..., max_length=100)
    constraints: str = Field(default="", max_length=2000)


class TestPromptRequest(BaseModel):
    prompt: str


class RefinePromptRequest(BaseModel):
    prompt: str
    action: str


class PromptResponse(BaseModel):
    prompt: str
    suggestions: Optional[List[str]] = None


class AIResponse(BaseModel):
    response: str