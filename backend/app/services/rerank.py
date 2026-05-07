from collections import Counter
from typing import Any


class RerankService:
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

    @staticmethod
    def _tokens(text: str) -> list[str]:
        normalized = "".join(ch.lower() if ch.isalnum() else " " for ch in text)
        return [token for token in normalized.split() if token]

