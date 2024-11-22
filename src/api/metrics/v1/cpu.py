"""
This module defines API routes for handling CPU-related data.
"""
from typing import List
from fastapi import APIRouter, Request
from domain.schemas import (
    ExceptionResponseSchema,
    GetCpuResponseSchema,
    GetCpuCoreResponseSchema,
)
from domain.services import CpuService

cpu_router = APIRouter()


@cpu_router.get(
    "/usage",
    response_model=List[GetCpuResponseSchema],
    # response_model_exclude={"id"},
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def get_cpu(request: Request) -> List[GetCpuResponseSchema]:
    """
    Route to get a list of CPU data.

    Args:
        request (Request): The incoming request.

    Returns:
        List[GetCpuResponseSchema]: A list of CPU data as per the response model.
    """
    return await CpuService().get_cpu(request.app.state.monitortask)


@cpu_router.get(
    "/core",
    response_model=GetCpuCoreResponseSchema,
    # response_model_exclude={"id"},
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def get_core_number(request: Request) -> GetCpuCoreResponseSchema:
    """
    Route to get the number of CPU core.

    Args:
        request (Request): The incoming request.

    Returns:
        int: number of cpu core.
    """
    return GetCpuCoreResponseSchema(number=request.app.state.monitortask.num_cores)
