from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field


@dataclass
class AgentContext:
    """Structured analysis produced by the AnalyzerAgent and consumed by all downstream agents."""

    mode: str  # "generate" | "correct"
    raw_prompt: str
    component_context: str  # raw component code when mode == "correct"
    detected_intent: str  # human-readable one-liner, e.g. "Generate a pricing card with Tailwind"
    use_tailwind: bool
    has_component_code: bool  # True when component_context contains actual JSX/TSX
    thread_history: list[dict[str, str]] = field(default_factory=list)


@dataclass
class ValidationResult:
    """Output produced by the ValidatorAgent."""

    valid: bool
    issues: list[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        if self.valid:
            return "Component is valid."
        return "Validation issues: " + "; ".join(self.issues)


class BaseAgent(ABC):
    """SRP: every concrete agent has a single responsibility and implements `execute`."""

    @abstractmethod
    async def execute(self, context: AgentContext) -> AsyncIterator[str]:
        """Stream response tokens.  Sync agents can yield nothing and just return."""
        ...  # pragma: no cover
