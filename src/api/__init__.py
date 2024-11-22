from fastapi import APIRouter
from api.metrics.v1.cpu import cpu_router as cpu_v1_router

router = APIRouter()
router.include_router(cpu_v1_router, prefix="/metrics/v1/cpu")

__all__ = ["router"]
