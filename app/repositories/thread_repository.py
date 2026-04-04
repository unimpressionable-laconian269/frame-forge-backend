from datetime import UTC, datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.domain import ThreadDocument


class ThreadRepository:
    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self.collection = database.threads

    async def create_thread(self, thread: ThreadDocument) -> ThreadDocument:
        await self.collection.insert_one(thread.model_dump())
        return thread

    async def get_thread(self, thread_id: str) -> ThreadDocument | None:
        document = await self.collection.find_one({"id": thread_id})
        return ThreadDocument(**document) if document else None

    async def list_threads(self) -> list[ThreadDocument]:
        cursor = self.collection.find({}).sort("updated_at", -1)
        documents = await cursor.to_list(length=200)
        return [ThreadDocument(**document) for document in documents]

    async def touch_thread(self, thread_id: str) -> None:
        await self.collection.update_one(
            {"id": thread_id},
            {"$set": {"updated_at": datetime.now(UTC)}},
        )

    async def delete_thread(self, thread_id: str) -> bool:
        result = await self.collection.delete_one({"id": thread_id})
        return result.deleted_count > 0
