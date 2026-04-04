from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.domain import MessageDocument


class MessageRepository:
    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self.collection = database.messages

    async def create_message(self, message: MessageDocument) -> MessageDocument:
        await self.collection.insert_one(message.model_dump())
        return message

    async def list_by_thread(self, thread_id: str) -> list[MessageDocument]:
        cursor = self.collection.find({"thread_id": thread_id}).sort("timestamp", 1)
        documents = await cursor.to_list(length=500)
        return [MessageDocument(**document) for document in documents]

    async def list_recent_by_thread(self, thread_id: str, limit: int) -> list[MessageDocument]:
        cursor = self.collection.find({"thread_id": thread_id}).sort("timestamp", -1).limit(limit)
        documents = await cursor.to_list(length=limit)
        ordered = reversed(documents)
        return [MessageDocument(**document) for document in ordered]

    async def delete_by_thread(self, thread_id: str) -> int:
        result = await self.collection.delete_many({"thread_id": thread_id})
        return result.deleted_count
