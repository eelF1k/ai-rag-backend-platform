from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import router as v1_router
from app.core.settings import settings
from app.db.lifecycle import close_connections
from app.db.sql import Base, engine
from app.observability.logging import logger


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("startup", env=settings.app_env)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as exc:  # keep API available in local/dev even if DB is down
        logger.warning("mysql_unavailable_on_startup", error=str(exc))
    yield
    await close_connections()
    logger.info("shutdown")


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(v1_router, prefix=settings.api_prefix)


@app.get("/")
async def root():
    return {
        "service": settings.app_name,
        "docs": "/docs",
        "health": f"{settings.api_prefix}/health",
    }
