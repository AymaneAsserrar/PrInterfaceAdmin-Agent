"""Module defining API routes for log metrics collection and analysis."""
import os
from typing import Dict

from fastapi import APIRouter, HTTPException, status
from domain.schemas import LogMetricsSchema, ExceptionResponseSchema
from domain.services import LogService

log_router = APIRouter()

# Environment configuration with defaults
ACCESS_LOG_PATH = os.getenv("ACCESS_LOG_PATH", "/app/logs/access.log")
ERROR_LOG_PATH = os.getenv("ERROR_LOG_PATH", "/app/logs/error.log")


@log_router.get(
    "/metrics",
    response_model=LogMetricsSchema,
    responses={
        200: {"description": "Successfully retrieved log metrics"},
        500: {"model": ExceptionResponseSchema},
    },
)
async def get_log_metrics() -> LogMetricsSchema:
    """
    Retrieve and analyze metrics from server log files.

    Returns:
        LogMetricsSchema: Aggregated metrics including request counts,
                         status codes, and recent errors

    Raises:
        HTTPException: If log analysis fails
    """
    try:
        service = LogService()
        return await service.get_log_metrics(
            access_log_path=ACCESS_LOG_PATH,
            error_log_path=ERROR_LOG_PATH,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze logs: {str(exc)}",
        ) from exc