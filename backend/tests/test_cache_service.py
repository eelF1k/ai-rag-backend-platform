import pytest

from app.services.cache import CacheService


class FakeRedis:
    def __init__(self):
        self.storage: dict[str, str] = {}

    async def get(self, key: str):
        return self.storage.get(key)

    async def set(self, key: str, value: str, ex: int | None = None):
        _ = ex
        self.storage[key] = value
        return True


@pytest.mark.asyncio
async def test_cache_service_json_roundtrip(monkeypatch):
    fake = FakeRedis()
    monkeypatch.setattr("app.services.cache.get_redis", lambda: fake)
    service = CacheService()

    key = service.search_key(query="invoice", limit=5)
    payload = {"query": "invoice", "hits": [{"id": "1"}]}
    await service.set_json(key, payload, ttl_s=10)

    restored = await service.get_json(key)
    assert restored == payload

