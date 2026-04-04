from typing import Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=8000)
    thread_id: str | None = None
    mode: Literal["generate", "correct"] = "generate"
    component_context: str | None = None


class ThreadSummary(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str


class MessageView(BaseModel):
    id: str
    thread_id: str
    role: str
    content: str
    code_snippet: str | None = None
    model_used: str | None = None
    timestamp: str
