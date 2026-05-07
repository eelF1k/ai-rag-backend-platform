from app.repositories import AuditEventRepository, IngestionJobRepository
from app.schemas.ingestion import IngestionRequest
from app.services.chunking import ChunkingService
from app.services.embeddings import EmbeddingsService


async def process_ingestion(job_id: int, payload: IngestionRequest) -> dict:
    jobs_repo = IngestionJobRepository()
    audit_repo = AuditEventRepository()
    chunking = ChunkingService()
    embeddings = EmbeddingsService()

    chunks = await chunking.chunk_text(
        text=payload.text,
        chunk_size=payload.chunk_size,
        overlap=payload.overlap,
    )
    index_result = await embeddings.index_chunks(source_name=payload.source_name, chunks=chunks)
    await jobs_repo.mark_processed(job_id=job_id, chunks_count=len(chunks))
    await audit_repo.add(
        actor="system",
        action="ingestion_complete",
        payload={
            "job_id": job_id,
            "source_name": payload.source_name,
            "chunks_count": len(chunks),
            "indexed": index_result["indexed"],
        },
    )
    return {"chunks": chunks, "indexed": index_result["indexed"]}

