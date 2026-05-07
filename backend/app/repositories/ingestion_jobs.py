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
