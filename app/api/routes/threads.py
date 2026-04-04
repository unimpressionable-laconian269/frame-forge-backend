from fastapi import APIRouter, Depends, HTTPException, Response

from app.api.dependencies import get_chat_service
from app.services.chat_service import ChatService

router = APIRouter()


@router.get("")
async def list_threads(chat_service: ChatService = Depends(get_chat_service)):
    return await chat_service.list_threads()


@router.get("/{thread_id}/messages")
async def list_messages(thread_id: str, chat_service: ChatService = Depends(get_chat_service)):
    thread_messages = await chat_service.list_messages(thread_id)
    if thread_messages is None:
        raise HTTPException(status_code=404, detail="Thread not found")
    return thread_messages


@router.delete("/{thread_id}", status_code=204)
async def delete_thread(thread_id: str, chat_service: ChatService = Depends(get_chat_service)) -> Response:
    deleted = await chat_service.delete_thread(thread_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Thread not found")
    return Response(status_code=204)
