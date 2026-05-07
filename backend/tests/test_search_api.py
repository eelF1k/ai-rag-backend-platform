from fastapi.testclient import TestClient

from app.main import app


def test_search_rerank_endpoint_with_strategy(monkeypatch):
    async def fake_search(self, query: str, limit: int = 5):
        _ = (self, query, limit)
        return {
            "documents": [["invoice billing details", "unrelated text"]],
            "metadatas": [[{"source_name": "doc-1"}, {"source_name": "doc-2"}]],
            "ids": [["1", "2"]],
            "distances": [[0.2, 1.1]],
        }

    monkeypatch.setattr("app.services.embeddings.EmbeddingsService.search", fake_search)

    with TestClient(app) as client:
        response = client.get(
            "/api/v1/search/rerank",
            params={"q": "invoice billing", "strategy": "hybrid", "limit": 1, "retrieval_limit": 5},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["strategy"] == "hybrid"
    assert len(payload["reranked_hits"]) == 1
    assert payload["reranked_hits"][0]["id"] == "1"

