from fastapi import APIRouter

from app.api.v1.ingestion import router as ingestion_router
from app.api.v1.ops import router as ops_router
from app.api.v1.system import router as system_router

router = APIRouter()
router.include_router(system_router)
router.include_router(ops_router)
router.include_router(ingestion_router)
