from __future__ import annotations

import re
from collections.abc import AsyncIterator

from app.agents.base import AgentContext, BaseAgent
from app.models.schemas import ChatRequest

_TAILWIND_HINTS = re.compile(
    r"\b(tailwind|tw-|bg-|text-|flex|grid|p-\d|m-\d|rounded|shadow|border-)\b",
    re.IGNORECASE,
)

_JSX_HINT = re.compile(r"<[A-Za-z][A-Za-z0-9]*[\s/>]|return\s*\(", re.MULTILINE)


class AnalyzerAgent(BaseAgent):
    async def execute(self, context: AgentContext) -> AsyncIterator[str]:  # type: ignore[override]
        return
        yield  # make this an async generator

    def analyze(self, request: ChatRequest, thread_history: list[dict[str, str]]) -> AgentContext:
        """Derive structured context from the incoming request."""
        combined_text = f"{request.prompt}\n{request.component_context or ''}"

        use_tailwind = bool(_TAILWIND_HINTS.search(combined_text))
        has_component_code = bool(
            request.component_context and _JSX_HINT.search(request.component_context)
        )

        if request.mode == "correct":
            detected_intent = (
                f"Repair the provided React component"
                + (f": {request.prompt}" if request.prompt else ".")
            )
        else:
            detected_intent = f"Generate a React component: {request.prompt}"

        return AgentContext(
            mode=request.mode,
            raw_prompt=request.prompt,
            component_context=request.component_context or "",
            detected_intent=detected_intent,
            use_tailwind=use_tailwind,
            has_component_code=has_component_code,
            thread_history=thread_history,
        )
