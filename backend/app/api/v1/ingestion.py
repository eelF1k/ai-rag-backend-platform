from time import perf_counter

from fastapi import APIRouter, HTTPException, status

from app.observability.metrics import increment_error, observe_latency
from app.repositories import AuditEventRepository, IngestionJobRepository
from app.schemas.ingestion import IngestionQueuedResponse, IngestionRequest, IngestionResponse
from app.services.ingestion_processor import process_ingestion
from app.services.queue import QueueService

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


@router.post("/text", response_model=IngestionResponse)
async def ingest_text(payload: IngestionRequest):
    started_at = perf_counter()
    jobs_repo = IngestionJobRepository()
    audit_repo = AuditEventRepository()

    job = await jobs_repo.create(source_name=payload.source_name)
    try:
        result = await process_ingestion(job_id=job.id, payload=payload)
        chunks = result["chunks"]
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


@router.post("/text/async", response_model=IngestionQueuedResponse)
async def ingest_text_async(payload: IngestionRequest):
    started_at = perf_counter()
    jobs_repo = IngestionJobRepository()
    audit_repo = AuditEventRepository()
    queue = QueueService()

    job = await jobs_repo.create(source_name=payload.source_name)
    try:
        await queue.enqueue_ingestion(
            {
                "job_id": job.id,
                "source_name": payload.source_name,
                "text": payload.text,
                "chunk_size": payload.chunk_size,
                "overlap": payload.overlap,
            }
        )
        await audit_repo.add(
            actor="system",
            action="ingestion_queued",
            payload={"job_id": job.id, "source_name": payload.source_name},
        )
    except Exception as exc:
        increment_error("ingestion_async_enqueue")
        await jobs_repo.mark_failed(job_id=job.id, error_message=str(exc))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Enqueue failed") from exc
    finally:
        observe_latency("ingestion_async_enqueue", started_at)

    return IngestionQueuedResponse(job_id=job.id, status="queued")

