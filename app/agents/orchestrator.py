from __future__ import annotations

from collections.abc import AsyncIterator

from app.agents.analyzer import AnalyzerAgent
from app.agents.base import AgentContext
from app.agents.corrector import CorrectorAgent
from app.agents.specialist import SpecialistAgent
from app.agents.validator import ValidatorAgent
from app.models.schemas import ChatRequest
from app.services.openrouter_service import OpenRouterService


class AgentOrchestrator:
    def __init__(self, openrouter_service: OpenRouterService) -> None:
        self._analyzer = AnalyzerAgent()
        self._specialist = SpecialistAgent(openrouter_service)
        self._corrector = CorrectorAgent(openrouter_service)
        self._validator = ValidatorAgent()

    async def stream(
        self,
        request: ChatRequest,
        thread_history: list[dict[str, str]],
    ) -> AsyncIterator[dict]:
        context: AgentContext = self._analyzer.analyze(request, thread_history)
        agent = self._corrector if context.mode == "correct" else self._specialist

        chunks: list[str] = []
        async for token in agent.execute(context):
            chunks.append(token)
            yield {"type": "token", "content": token}

        full_response = "".join(chunks).strip()
        validation = self._validator.validate(full_response)

        if not validation.valid:
            warning = f"\n\n>Validation note: {validation.summary}"
            for char in warning:
                yield {"type": "token", "content": char}
            full_response += warning

        yield {"type": "full_response", "content": full_response}
