from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.db.sql import engine
from app.models.ingestion_job import IngestionJob

session_factory = async_sessionmaker(engine, expire_on_commit=False)


class IngestionJobRepository:
    async def create(self, source_name: str) -> IngestionJob:
        async with session_factory() as session:
            job = IngestionJob(source_name=source_name, status="queued")
            session.add(job)
            await session.commit()
            await session.refresh(job)
            return job

    async def list_recent(self, limit: int = 20) -> list[IngestionJob]:
        async with session_factory() as session:
            result = await session.execute(select(IngestionJob).order_by(IngestionJob.id.desc()).limit(limit))
            return list(result.scalars().all())

    async def mark_processed(self, job_id: int, chunks_count: int) -> IngestionJob | None:
        async with session_factory() as session:
            result = await session.execute(select(IngestionJob).where(IngestionJob.id == job_id))
            job = result.scalar_one_or_none()
            if job is None:
                return None

            job.status = "processed"
            job.chunks_count = chunks_count
            job.error_message = None
            await session.commit()
            await session.refresh(job)
            return job

    async def mark_failed(self, job_id: int, error_message: str) -> IngestionJob | None:
        async with session_factory() as session:
            result = await session.execute(select(IngestionJob).where(IngestionJob.id == job_id))
            job = result.scalar_one_or_none()
            if job is None:
                return None

            job.status = "failed"
            job.error_message = error_message
            await session.commit()
            await session.refresh(job)
            return job
