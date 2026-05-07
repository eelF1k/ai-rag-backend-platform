from time import perf_counter

from fastapi import APIRouter

from app.observability.metrics import increment_error, observe_latency
from app.schemas.rag import RAGAnswerRequest, RAGAnswerResponse
from app.services.embeddings import EmbeddingsService
from app.services.llm import LLMService
from app.services.rerank import RerankService

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/answer", response_model=RAGAnswerResponse)
async def rag_answer(payload: RAGAnswerRequest):
    started_at = perf_counter()
    try:
        retrieval_limit = min(max(payload.top_k * 3, payload.top_k), 50)
        retrieval_service = EmbeddingsService()
        retrieval_result = await retrieval_service.search(query=payload.question, limit=retrieval_limit)

        documents = retrieval_result.get("documents", [[]])[0]
        metadatas = retrieval_result.get("metadatas", [[]])[0]
        ids = retrieval_result.get("ids", [[]])[0]
        distances = retrieval_result.get("distances", [[]])[0] if "distances" in retrieval_result else []

        hits = []
        for idx, doc in enumerate(documents):
            hits.append(
                {
                    "id": ids[idx] if idx < len(ids) else None,
                    "text": doc,
                    "metadata": metadatas[idx] if idx < len(metadatas) else {},
                    "distance": distances[idx] if idx < len(distances) else None,
                }
            )

        reranked = RerankService().rerank(
            query=payload.question,
            hits=hits,
            limit=payload.top_k,
            strategy=payload.strategy,
        )

        llm_response = await LLMService().generate_answer(
            question=payload.question,
            contexts=reranked,
        )

        return RAGAnswerResponse(
            answer=llm_response["answer"],
            provider=str(llm_response["provider"]),
            used_fallback=bool(llm_response["used_fallback"]),
            contexts_used=len(reranked),
            contexts=reranked,
        )
    except Exception:
        increment_error("rag_answer")
        raise
    finally:
        observe_latency("rag_answer", started_at)

