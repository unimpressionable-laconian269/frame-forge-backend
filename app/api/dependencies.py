from collections.abc import AsyncGenerator

from fastapi import Depends

from app.agents.orchestrator import AgentOrchestrator
from app.core.config import Settings, get_settings
from app.db.mongo import get_database
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.thread_repository import ThreadRepository
from app.services.chat_service import ChatService
from app.services.openrouter_service import OpenRouterService


def get_app_settings() -> Settings:
    return get_settings()


async def get_chat_service(
    settings: Settings = Depends(get_app_settings),
) -> AsyncGenerator[ChatService, None]:
    database = get_database()
    openrouter_service = OpenRouterService(settings)
    service = ChatService(
        thread_repository=ThreadRepository(database),
        message_repository=MessageRepository(database),
        audit_log_repository=AuditLogRepository(database),
        openrouter_service=openrouter_service,
        agent_orchestrator=AgentOrchestrator(openrouter_service),
        settings=settings,
    )
    yield service
