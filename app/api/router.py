from fastapi import APIRouter

from app.api.routes import chat, threads

api_router = APIRouter()
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(threads.router, prefix="/threads", tags=["threads"])
