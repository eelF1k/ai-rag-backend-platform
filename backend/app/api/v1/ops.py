from fastapi import APIRouter, Query

from app.repositories import AuditEventRepository, IngestionJobRepository

router = APIRouter(prefix="/ops", tags=["ops"])


@router.post("/jobs")
async def create_job(source_name: str = Query(..., min_length=1)):
    jobs_repo = IngestionJobRepository()
    audit_repo = AuditEventRepository()

    job = await jobs_repo.create(source_name=source_name)
    await audit_repo.add(actor="system", action="create_job", payload={"job_id": job.id, "source_name": source_name})

    return {
        "job_id": job.id,
        "source_name": job.source_name,
        "status": job.status,
    }


@router.get("/jobs")
async def list_jobs(limit: int = Query(20, ge=1, le=100)):
    jobs_repo = IngestionJobRepository()
    jobs = await jobs_repo.list_recent(limit=limit)
    return [
        {
            "id": job.id,
            "source_name": job.source_name,
            "status": job.status,
            "chunks_count": job.chunks_count,
            "error_message": job.error_message,
        }
        for job in jobs
    ]


@router.get("/audit")
async def list_audit(limit: int = Query(20, ge=1, le=100)):
    audit_repo = AuditEventRepository()
    return await audit_repo.list_recent(limit=limit)
