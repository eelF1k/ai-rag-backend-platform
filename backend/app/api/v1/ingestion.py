from time import perf_counter

from fastapi import APIRouter, HTTPException, status

from app.observability.metrics import increment_error, observe_latency
from app.repositories import AuditEventRepository, IngestionJobRepository
from app.schemas.ingestion import IngestionRequest, IngestionResponse
from app.services.chunking import ChunkingService
from app.services.embeddings import EmbeddingsService

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


@router.post("/text", response_model=IngestionResponse)
async def ingest_text(payload: IngestionRequest):
    started_at = perf_counter()
    jobs_repo = IngestionJobRepository()
    audit_repo = AuditEventRepository()
    chunking = ChunkingService()
    embeddings = EmbeddingsService()

    job = await jobs_repo.create(source_name=payload.source_name)
    try:
        chunks = await chunking.chunk_text(
            text=payload.text,
            chunk_size=payload.chunk_size,
            overlap=payload.overlap,
        )
        index_result = await embeddings.index_chunks(source_name=payload.source_name, chunks=chunks)
        await jobs_repo.mark_processed(job_id=job.id, chunks_count=len(chunks))
        await audit_repo.add(
            actor="system",
            action="ingestion_complete",
            payload={
                "job_id": job.id,
                "source_name": payload.source_name,
                "chunks_count": len(chunks),
                "indexed": index_result["indexed"],
            },
        )
    except Exception as exc:
        increment_error("ingestion_text")
        await jobs_repo.mark_failed(job_id=job.id, error_message=str(exc))
        await audit_repo.add(
            actor="system",
            action="ingestion_failed",
            payload={"job_id": job.id, "source_name": payload.source_name, "error": str(exc)},
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ingestion failed") from exc
    finally:
        observe_latency("ingestion_text", started_at)

    preview = chunks[:3]
    return IngestionResponse(
        job_id=job.id,
        status="processed",
        chunks_count=len(chunks),
        preview_chunks=preview,
    )

