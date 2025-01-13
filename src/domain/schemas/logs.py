"""
This module defines response schemas for log-related data.
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List


class LogEntrySchema(BaseModel):
    """Schema for individual log entries."""
    timestamp: datetime
    ip: str
    url: str
    status_code: int
    user_agent: str


class LogMetricsSchema(BaseModel):
    """Schema for aggregated log metrics."""
    total_requests: int
    success_count: int
    error_count: int
    status_codes: Dict[str, int]
    top_urls: List[Dict[str, str | int]]
    recent_errors: List[LogEntrySchema]