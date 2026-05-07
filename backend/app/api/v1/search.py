from fastapi import APIRouter, Query

from app.services.embeddings import EmbeddingsService
from app.services.rerank import RerankService

router = APIRouter(prefix="/search", tags=["search"])


@router.get("")
async def search_documents(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(5, ge=1, le=20),
):
    """
    Raw vector retrieval from Chroma without reranking.
    """
    service = EmbeddingsService()
    result = await service.search(query=q, limit=limit)

    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    ids = result.get("ids", [[]])[0]
    distances = result.get("distances", [[]])[0] if "distances" in result else []

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
    return {"query": q, "hits": hits}


@router.get("/rerank")
async def search_with_rerank(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(5, ge=1, le=20),
    retrieval_limit: int = Query(15, ge=5, le=50),
):
    """
    Two-step retrieval:
    1) vector search from Chroma
    2) lexical rerank fallback service
    """
    retrieval = await search_documents(q=q, limit=retrieval_limit)
    reranker = RerankService()
    reranked_hits = reranker.rerank(query=q, hits=retrieval["hits"], limit=limit)

    return {
        "query": q,
        "retrieval_limit": retrieval_limit,
        "reranked_hits": reranked_hits,
    }

