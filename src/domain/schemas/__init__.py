from pydantic import BaseModel
from .cpu import GetCpuResponseSchema, GetCpuCoreResponseSchema


class ExceptionResponseSchema(BaseModel):
    error: str


__all__ = [
    "GetCpuResponseSchema",
    "GetCpuCoreResponseSchema",
    "ExceptionResponseSchema",
]
