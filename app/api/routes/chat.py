import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_chat_service
from app.models.schemas import ChatRequest
from app.services.chat_service import ChatService

router = APIRouter()


async def ndjson_stream(chat_service: ChatService, request: ChatRequest) -> AsyncIterator[str]:
    async for event in chat_service.stream_chat(request):
        yield json.dumps(event) + "\n"


@router.post("/stream")
async def stream_chat(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
) -> StreamingResponse:
    return StreamingResponse(ndjson_stream(chat_service, request), media_type="application/x-ndjson")
