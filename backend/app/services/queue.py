import json
from typing import Any

from app.db.redis import get_redis

INGESTION_QUEUE = "ingestion:queue"


class QueueService:
    async def enqueue_ingestion(self, message: dict[str, Any]) -> None:
        await get_redis().rpush(INGESTION_QUEUE, json.dumps(message, ensure_ascii=True))

    async def pop_ingestion(self, timeout_s: int = 5) -> dict[str, Any] | None:
        item = await get_redis().blpop([INGESTION_QUEUE], timeout=timeout_s)
        if not item:
            return None
        _, payload = item
        return json.loads(payload)

