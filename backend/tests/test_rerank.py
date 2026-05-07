from app.services.rerank import HybridReranker, LexicalReranker


def test_lexical_reranker_prefers_token_overlap():
    reranker = LexicalReranker()
    hits = [
        {"id": "a", "text": "apple banana grape", "distance": 0.9},
        {"id": "b", "text": "apple apple banana", "distance": 1.2},
    ]

    result = reranker.rerank(query="apple banana", hits=hits, limit=2)

    assert len(result) == 2
    assert result[0]["id"] == "a"
    assert result[0]["rerank_score"] >= result[1]["rerank_score"]


def test_hybrid_reranker_returns_hybrid_score_field():
    reranker = HybridReranker(lexical_weight=0.5, vector_weight=0.5)
    hits = [
        {"id": "a", "text": "invoice payment status", "distance": 0.3},
        {"id": "b", "text": "subscription invoice billing", "distance": 0.6},
    ]

    result = reranker.rerank(query="invoice billing", hits=hits, limit=2)

    assert len(result) == 2
    assert "hybrid_score" in result[0]
    assert "vector_score" in result[0]
    assert "lexical_score" in result[0]

