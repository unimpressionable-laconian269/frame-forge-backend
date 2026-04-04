from __future__ import annotations

from collections.abc import AsyncIterator

from app.agents.base import AgentContext, BaseAgent
from app.services.openrouter_service import OpenRouterService

_GENERATION_SYSTEM_PROMPT = """
You are a senior React engineer specialised in building clean, self-contained UI components.

Rules:
- Answer in English at all times.
- Start with ONE concise sentence describing what you are building (no headings).
- Then output exactly ONE fenced code block tagged `tsx`.
- The code block must contain a SINGLE FILE with ALL components defined inline — no multi-file structure.
- NEVER import from local paths like ./components/X, ../utils, etc. Everything must be in one file.
- NEVER split code across multiple files or reference helper files.
- Only allowed import: `import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';`
- The last exported symbol must be the main component exported as `export default`.
- If you need sub-components (e.g. Card, Header, Section), define them as const inside the same file BEFORE the main component.
- All sample data must be inlined as constants in the file; do not rely on external state or APIs.
- Provide safe default parameter values for every prop so the component renders without external data.
- Only use Tailwind utility classes when the user explicitly requests Tailwind.
- Otherwise, use concise inline styles. Do NOT reference any .css file.
- Do NOT wrap the answer in markdown headings or extra prose after the code block.
- Do NOT use React.lazy, React.Suspense, dynamic import(), or any async rendering.
""".strip()


class SpecialistAgent(BaseAgent):
    def __init__(self, openrouter_service: OpenRouterService) -> None:
        self._openrouter = openrouter_service

    async def execute(self, context: AgentContext) -> AsyncIterator[str]:  # type: ignore[override]
        messages = [{"role": "system", "content": _GENERATION_SYSTEM_PROMPT}]
        messages.extend(context.thread_history)
        messages.append({"role": "user", "content": context.detected_intent})

        async for token in self._openrouter.stream_chat(messages):
            yield token
