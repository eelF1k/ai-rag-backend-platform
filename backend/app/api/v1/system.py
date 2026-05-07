from fastapi import APIRouter, Response

from app.core.settings import settings
from app.observability.metrics import render_metrics

router = APIRouter()


@router.get("/health", tags=["system"])
async def healthcheck():
    return {
        "status": "ok",
        "service": settings.app_name,
        "env": settings.app_env,
    }


@router.get("/ready", tags=["system"])
async def readiness():
    # At next steps we'll add real checks for MySQL/Mongo/Redis/Chroma
    return {"ready": True}


@router.get("/metrics", tags=["system"])
async def metrics():
    payload, content_type = render_metrics()
    return Response(content=payload, media_type=content_type)
