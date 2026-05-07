import asyncio

from app.observability.logging import logger
from app.repositories import AuditEventRepository, IngestionJobRepository
from app.schemas.ingestion import IngestionRequest
from app.services.ingestion_processor import process_ingestion
from app.services.queue import QueueService


async def process_next_message() -> bool:
    queue = QueueService()
    message = await queue.pop_ingestion(timeout_s=1)
    if not message:
        return False

    job_id = int(message["job_id"])
    payload = IngestionRequest(
        source_name=str(message["source_name"]),
        text=str(message["text"]),
        chunk_size=int(message["chunk_size"]),
        overlap=int(message["overlap"]),
    )

    jobs_repo = IngestionJobRepository()
    audit_repo = AuditEventRepository()

    try:
        await process_ingestion(job_id=job_id, payload=payload)
        logger.info("ingestion_worker_processed", job_id=job_id)
    except Exception as exc:
        await jobs_repo.mark_failed(job_id=job_id, error_message=str(exc))
        await audit_repo.add(
            actor="worker",
            action="ingestion_failed",
            payload={"job_id": job_id, "error": str(exc)},
        )
        logger.warning("ingestion_worker_failed", job_id=job_id, error=str(exc))
    return True


async def run_forever() -> None:
    logger.info("ingestion_worker_started")
    while True:
        processed = await process_next_message()
        if not processed:
            await asyncio.sleep(0.2)


if __name__ == "__main__":
    asyncio.run(run_forever())

