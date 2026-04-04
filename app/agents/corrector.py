from __future__ import annotations

from collections.abc import AsyncIterator

from app.agents.base import AgentContext, BaseAgent
from app.services.openrouter_service import OpenRouterService

_CORRECTION_SYSTEM_PROMPT = """
You are a senior React engineer specialised in debugging and repairing UI components.

Rules:
- Answer in English at all times.
- Start with ONE concise sentence summarising the issue you found (no headings).
- Then output exactly ONE fenced code block tagged `tsx`.
- The code block must contain the fully corrected component exported as `default`.
- Preserve the original intent, structure, and naming of the component.
- Fix ALL issues: runtime errors, missing default exports, broken props, invalid JSX.
- Ensure every prop has a safe default value so the component renders without external data.
- Do NOT import from node_modules except `react`.
- Do NOT use Tailwind unless the original component already uses it.
- Do NOT wrap the answer in markdown headings or extra prose after the code block.
""".strip()


class CorrectorAgent(BaseAgent):
    def __init__(self, openrouter_service: OpenRouterService) -> None:
        self._openrouter = openrouter_service

    async def execute(self, context: AgentContext) -> AsyncIterator[str]:  # type: ignore[override]
        user_content = self._build_user_content(context)

        messages = [{"role": "system", "content": _CORRECTION_SYSTEM_PROMPT}]
        messages.extend(context.thread_history)
        messages.append({"role": "user", "content": user_content})

        async for token in self._openrouter.stream_chat(messages):
            yield token

    @staticmethod
    def _build_user_content(context: AgentContext) -> str:
        parts: list[str] = []

        if context.component_context:
            parts.append("Here is the component that needs to be repaired:")
            parts.append(f"```tsx\n{context.component_context}\n```")

        if context.raw_prompt:
            parts.append(f"Additional instructions: {context.raw_prompt}")
        else:
            parts.append("Fix all bugs and ensure the component renders correctly with safe default props.")

        return "\n\n".join(parts)
