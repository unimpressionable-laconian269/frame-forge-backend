from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.domain import AuditLogDocument


class AuditLogRepository:
    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self.collection = database.audit_logs

    async def create_log(self, log: AuditLogDocument) -> AuditLogDocument:
        await self.collection.insert_one(log.model_dump())
        return log
