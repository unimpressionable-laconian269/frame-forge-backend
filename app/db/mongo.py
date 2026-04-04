from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import Settings

client: AsyncIOMotorClient | None = None
database: AsyncIOMotorDatabase | None = None


async def connect_to_mongo(settings: Settings) -> None:
    global client, database
    client = AsyncIOMotorClient(settings.mongo_uri)
    database = client[settings.mongo_db_name]

    await database.threads.create_index("updated_at")
    await database.messages.create_index([("thread_id", 1), ("timestamp", 1)])
    await database.audit_logs.create_index("timestamp")


async def close_mongo_connection() -> None:
    global client, database
    if client is not None:
        client.close()
    client = None
    database = None


def get_database() -> AsyncIOMotorDatabase:
    if database is None:
        raise RuntimeError("Mongo database has not been initialized")
    return database
