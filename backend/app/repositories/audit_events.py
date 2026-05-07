from datetime import datetime, timezone
from typing import Any

from app.db.mongo import database


class AuditEventRepository:
    collection = database["audit_events"]

    async def add(self, actor: str, action: str, payload: dict[str, Any]) -> str:
        result = await self.collection.insert_one(
            {
                "actor": actor,
                "action": action,
                "payload": payload,
                "created_at": datetime.now(timezone.utc),
            }
        )
        return str(result.inserted_id)

    async def list_recent(self, limit: int = 20) -> list[dict[str, Any]]:
        cursor = self.collection.find({}, {"_id": 0}).sort("created_at", -1).limit(limit)
        return [doc async for doc in cursor]
