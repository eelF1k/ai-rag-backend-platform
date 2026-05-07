from fastapi import APIRouter, Query

from app.services.embeddings import EmbeddingsService

router = APIRouter(prefix="/search", tags=["search"])


@router.get("")
async def search_documents(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(5, ge=1, le=20),
):
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

