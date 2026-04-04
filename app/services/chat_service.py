from collections.abc import AsyncIterator

from app.agents.orchestrator import AgentOrchestrator
from app.core.config import Settings
from app.models.domain import AuditLogDocument, MessageDocument, ThreadDocument
from app.models.schemas import ChatRequest
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.thread_repository import ThreadRepository
from app.services.code_parser import extract_code_block, strip_code_blocks
from app.services.openrouter_service import OpenRouterService


class ChatService:
    def __init__(
        self,
        thread_repository: ThreadRepository,
        message_repository: MessageRepository,
        audit_log_repository: AuditLogRepository,
        openrouter_service: OpenRouterService,
        agent_orchestrator: AgentOrchestrator,
        settings: Settings,
    ) -> None:
        self.thread_repository = thread_repository
        self.message_repository = message_repository
        self.audit_log_repository = audit_log_repository
        self.openrouter_service = openrouter_service
        self.agent_orchestrator = agent_orchestrator
        self.settings = settings

    async def list_threads(self) -> list[dict[str, str]]:
        threads = await self.thread_repository.list_threads()
        return [self._serialize_thread(thread) for thread in threads]

    async def list_messages(self, thread_id: str) -> list[dict[str, str]] | None:
        thread = await self.thread_repository.get_thread(thread_id)
        if thread is None:
            return None
        messages = await self.message_repository.list_by_thread(thread_id)
        return [self._serialize_message(message) for message in messages]

    async def delete_thread(self, thread_id: str) -> bool:
        thread = await self.thread_repository.get_thread(thread_id)
        if thread is None:
            return False

        await self.message_repository.delete_by_thread(thread_id)
        deleted = await self.thread_repository.delete_thread(thread_id)

        if deleted:
            await self.audit_log_repository.create_log(
                AuditLogDocument(
                    event_type="thread_deleted",
                    details={"thread_id": thread_id},
                )
            )

        return deleted

    async def stream_chat(self, request: ChatRequest) -> AsyncIterator[dict]:
        thread = await self._get_or_create_thread(request)
        user_message = MessageDocument(
            thread_id=thread.id,
            role="user",
            content=request.prompt or request.component_context or "Fix component",
            metadata={"mode": request.mode, "component_context": request.component_context},
        )
        await self.message_repository.create_message(user_message)
        await self.thread_repository.touch_thread(thread.id)

        yield {"type": "thread", "thread": self._serialize_thread(thread)}
        yield {"type": "message", "message": self._serialize_message(user_message)}

        recent_messages = await self.message_repository.list_recent_by_thread(
            thread.id,
            self.settings.max_context_messages,
        )
        thread_history = [
            {
                "role": msg.role,
                "content": self._to_llm_content(msg.content, msg.metadata),
            }
            for msg in recent_messages
            if msg.id != user_message.id
        ]

        full_response_parts: list[str] = []
        try:
            async for event in self.agent_orchestrator.stream(request, thread_history):
                if event["type"] == "token":
                    full_response_parts.append(event["content"])
                    yield event
                elif event["type"] == "full_response":
                    # The orchestrator already aggregated this; we overwrite to ensure consistency.
                    full_response_parts = [event["content"]]

            full_response = "".join(full_response_parts).strip()
            assistant_message = MessageDocument(
                thread_id=thread.id,
                role="assistant",
                content=strip_code_blocks(full_response),
                code_snippet=extract_code_block(full_response),
                model_used=self.settings.openrouter_model,
                metadata={"raw_response": full_response, "mode": request.mode},
            )
            await self.message_repository.create_message(assistant_message)
            await self.thread_repository.touch_thread(thread.id)
            await self.audit_log_repository.create_log(
                AuditLogDocument(
                    event_type="api_call",
                    details={
                        "thread_id": thread.id,
                        "mode": request.mode,
                        "model": self.settings.openrouter_model,
                        "agent": "corrector" if request.mode == "correct" else "specialist",
                    },
                )
            )
            yield {"type": "done", "message": self._serialize_message(assistant_message)}
        except Exception as exc:
            await self.audit_log_repository.create_log(
                AuditLogDocument(
                    event_type="error",
                    details={"thread_id": thread.id, "error": str(exc)},
                )
            )
            yield {"type": "error", "error": str(exc)}

    async def _get_or_create_thread(self, request: ChatRequest) -> ThreadDocument:
        if request.thread_id:
            thread = await self.thread_repository.get_thread(request.thread_id)
            if thread is not None:
                return thread

        title = self._build_thread_title(request.prompt)
        thread = ThreadDocument(title=title)
        await self.thread_repository.create_thread(thread)
        return thread

    @staticmethod
    def _build_thread_title(prompt: str) -> str:
        normalized = " ".join(prompt.split())
        if len(normalized) <= 48:
            return normalized
        return normalized[:45].rstrip() + "..."

    @staticmethod
    def _to_llm_content(content: str, metadata: dict) -> str:
        mode = metadata.get("mode")
        component_context = metadata.get("component_context")
        if mode == "correct" and component_context:
            return f"User request: {content}\n\nCode to fix:\n{component_context}"
        return content

    @staticmethod
    def _serialize_thread(thread: ThreadDocument) -> dict[str, str]:
        return {
            "id": thread.id,
            "title": thread.title,
            "created_at": thread.created_at.isoformat(),
            "updated_at": thread.updated_at.isoformat(),
        }

    @staticmethod
    def _serialize_message(message: MessageDocument) -> dict[str, str | None]:
        return {
            "id": message.id,
            "thread_id": message.thread_id,
            "role": message.role,
            "content": message.content,
            "code_snippet": message.code_snippet,
            "model_used": message.model_used,
            "timestamp": message.timestamp.isoformat(),
        }
