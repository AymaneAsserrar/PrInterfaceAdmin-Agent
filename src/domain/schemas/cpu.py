"""
This module defines a data transfer model for a GetCpuResponseSchema.
"""
from pydantic import BaseModel, Field

class GetCpuResponseSchema(BaseModel):
    core: int = Field(..., ge=0)
    usage: float = Field(..., ge=0, le=100)

class GetCpuCoreResponseSchema(BaseModel):
    number: int = Field(..., gt=0)

class ExceptionResponseSchema(BaseModel):
    detail: str