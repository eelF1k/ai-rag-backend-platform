from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import router as v1_router
from app.core.settings import settings
from app.observability.logging import logger


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("startup", env=settings.app_env)
    yield
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
