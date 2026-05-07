from collections import Counter
from abc import ABC, abstractmethod
from typing import Any


class BaseReranker(ABC):
    @abstractmethod
    def rerank(self, query: str, hits: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
        raise NotImplementedError

    @staticmethod
    def _tokens(text: str) -> list[str]:
        normalized = "".join(ch.lower() if ch.isalnum() else " " for ch in text)
        return [token for token in normalized.split() if token]


class LexicalReranker(BaseReranker):
    """
    Lightweight lexical reranker used as a deterministic fallback.
    Later this can be replaced by cross-encoder/LLM reranker.
    """

    def rerank(self, query: str, hits: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
        scored: list[tuple[float, dict[str, Any]]] = []
        query_tokens = self._tokens(query)
        query_counter = Counter(query_tokens)

        for hit in hits:
            text = str(hit.get("text", ""))
            text_tokens = self._tokens(text)
            text_counter = Counter(text_tokens)

            overlap = sum(min(query_counter[token], text_counter[token]) for token in query_counter)
            density = overlap / max(1, len(text_tokens))

            base_distance = hit.get("distance")
            distance_penalty = float(base_distance) if isinstance(base_distance, (float, int)) else 0.0

            score = (overlap * 2.0) + (density * 5.0) - distance_penalty
            enriched = {**hit, "rerank_score": round(score, 4), "token_overlap": overlap}
            scored.append((score, enriched))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [entry for _, entry in scored[:limit]]


class HybridReranker(BaseReranker):
    """
    Hybrid reranker:
    combines lexical relevance and vector similarity in one score.
    """

    def __init__(self, lexical_weight: float = 0.6, vector_weight: float = 0.4):
        self.lexical_weight = lexical_weight
        self.vector_weight = vector_weight

    def rerank(self, query: str, hits: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
        if not hits:
            return []

        lexical = LexicalReranker()
        lexical_scored = lexical.rerank(query=query, hits=hits, limit=len(hits))

        max_lex = max((float(item.get("rerank_score", 0.0)) for item in lexical_scored), default=1.0)
        max_lex = max(max_lex, 1e-9)

        scored: list[tuple[float, dict[str, Any]]] = []
        for hit in lexical_scored:
            lex_score = float(hit.get("rerank_score", 0.0)) / max_lex

            distance = hit.get("distance")
            if isinstance(distance, (float, int)):
                vector_score = 1.0 / (1.0 + float(distance))
            else:
                vector_score = 0.0

            hybrid_score = (self.lexical_weight * lex_score) + (self.vector_weight * vector_score)

            enriched = {
                **hit,
                "lexical_score": round(lex_score, 4),
                "vector_score": round(vector_score, 4),
                "hybrid_score": round(hybrid_score, 4),
            }
            scored.append((hybrid_score, enriched))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [entry for _, entry in scored[:limit]]


class RerankService:
    """
    Facade for reranking strategies.
    """

    _STRATEGIES = {
        "lexical": LexicalReranker,
        "hybrid": HybridReranker,
    }

    def rerank(
        self,
        query: str,
        hits: list[dict[str, Any]],
        limit: int,
        strategy: str = "hybrid",
    ) -> list[dict[str, Any]]:
        reranker_cls = self._STRATEGIES.get(strategy, HybridReranker)
        reranker = reranker_cls()
        return reranker.rerank(query=query, hits=hits, limit=limit)

