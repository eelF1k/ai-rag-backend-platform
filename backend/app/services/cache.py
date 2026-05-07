import hashlib
import json
from typing import Any

from app.core.settings import settings
from app.db.redis import get_redis


class CacheService:
    def _make_key(self, prefix: str, payload: dict[str, Any]) -> str:
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=True)
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]
        return f"cache:{prefix}:{digest}"

    async def get_json(self, key: str) -> dict[str, Any] | None:
        value = await get_redis().get(key)
        if not value:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return None

    async def set_json(self, key: str, payload: dict[str, Any], ttl_s: int | None = None) -> None:
        ttl = ttl_s if ttl_s is not None else settings.cache_ttl_s
        await get_redis().set(key, json.dumps(payload, ensure_ascii=True), ex=ttl)

    def search_key(self, query: str, limit: int) -> str:
        return self._make_key("search", {"q": query, "limit": limit})

    def rerank_key(self, query: str, limit: int, retrieval_limit: int, strategy: str) -> str:
        return self._make_key(
            "rerank",
            {"q": query, "limit": limit, "retrieval_limit": retrieval_limit, "strategy": strategy},
        )

    def rag_key(self, question: str, top_k: int, strategy: str) -> str:
        return self._make_key("rag", {"question": question, "top_k": top_k, "strategy": strategy})

