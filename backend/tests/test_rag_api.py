from fastapi.testclient import TestClient

from app.main import app


def test_rag_answer_uses_mocked_retrieval_and_llm(monkeypatch):
    async def fake_search(self, query: str, limit: int = 5):
        _ = (self, query, limit)
        return {
            "documents": [["invoice for april", "subscription plan details"]],
            "metadatas": [[{"source_name": "doc-1"}, {"source_name": "doc-2"}]],
            "ids": [["1", "2"]],
            "distances": [[0.2, 0.5]],
        }

    async def fake_generate_answer(self, question: str, contexts: list[dict]):
        _ = (self, question, contexts)
        return {"answer": "mocked answer", "provider": "mock", "used_fallback": False}

    monkeypatch.setattr("app.services.embeddings.EmbeddingsService.search", fake_search)
    monkeypatch.setattr("app.services.llm.LLMService.generate_answer", fake_generate_answer)

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/rag/answer",
            json={"question": "What about invoice?", "top_k": 1, "strategy": "hybrid"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"] == "mocked answer"
    assert payload["provider"] == "mock"
    assert payload["contexts_used"] == 1


def test_rag_answer_uses_cache_when_available(monkeypatch):
    async def fake_get_json(self, key: str):
        _ = (self, key)
        return {
            "answer": "cached rag answer",
            "provider": "cache",
            "used_fallback": False,
            "contexts_used": 1,
            "contexts": [{"id": "ctx-1", "text": "cached context"}],
        }

    async def fail_generate_answer(self, question: str, contexts: list[dict]):
        _ = (self, question, contexts)
        raise AssertionError("LLM should not be called on cache hit")

    monkeypatch.setattr("app.services.cache.CacheService.get_json", fake_get_json)
    monkeypatch.setattr("app.services.llm.LLMService.generate_answer", fail_generate_answer)

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/rag/answer",
            json={"question": "What about invoice?", "top_k": 1, "strategy": "hybrid"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"] == "cached rag answer"
    assert payload["provider"] == "cache"

