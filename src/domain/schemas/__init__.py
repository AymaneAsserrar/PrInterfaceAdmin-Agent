from pydantic import BaseModel
from .cpu import GetCpuResponseSchema, GetCpuCoreResponseSchema
from .ram import GetRamResponseSchema, GetRamInfoResponseSchema


class ExceptionResponseSchema(BaseModel):
    error: str


__all__ = [
    "GetCpuResponseSchema",
    "GetCpuCoreResponseSchema",
    "GetRamResponseSchema", 
    "GetRamInfoResponseSchema",
    "ExceptionResponseSchema",
]