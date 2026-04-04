from datetime import UTC, datetime
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field

Role = Literal["system", "user", "assistant"]


class ThreadDocument(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str | None = None
    title: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class MessageDocument(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    thread_id: str
    role: Role
    content: str
    code_snippet: str | None = None
    model_used: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AuditLogDocument(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str
    details: dict[str, Any]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
