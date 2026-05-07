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

