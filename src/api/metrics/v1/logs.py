"""
This module defines API routes for log metrics.
"""
from fastapi import APIRouter, HTTPException, status
from domain.schemas import LogMetricsSchema, ExceptionResponseSchema
from domain.services import LogService

log_router = APIRouter()


@log_router.get(
    "/metrics",
    response_model=LogMetricsSchema,
    responses={
        200: {"description": "Successfully retrieved log metrics"},
        500: {"model": ExceptionResponseSchema}
    }
)
async def get_log_metrics() -> LogMetricsSchema:
    """
    Get metrics from the log file including success and error counts,
    status code distribution, top URLs, and recent errors.
    
    Returns:
        LogMetricsSchema: Aggregated log metrics including counts, top URLs, and recent errors
    """
    try:
        service = LogService()
        return await service.get_log_metrics()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze logs: {str(e)}"
        )