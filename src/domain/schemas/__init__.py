from pydantic import BaseModel
from .cpu import GetCpuResponseSchema, GetCpuCoreResponseSchema
from .ram import GetRamResponseSchema, GetRamInfoResponseSchema
from .logs import LogEntrySchema, LogMetricsSchema

class ExceptionResponseSchema(BaseModel):
    error: str


__all__ = [
    "GetCpuResponseSchema",
    "GetCpuCoreResponseSchema",
    "GetRamResponseSchema",
    "GetRamInfoResponseSchema",
    "LogEntrySchema",
    "LogMetricsSchema",
    "ExceptionResponseSchema",
]