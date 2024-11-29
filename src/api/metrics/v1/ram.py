"""
This module defines API routes for handling RAM-related data.
"""
from typing import List
from fastapi import APIRouter, Request
from domain.schemas import (
    ExceptionResponseSchema,
    GetRamResponseSchema,
    GetRamInfoResponseSchema,
)
from domain.services import RamService

ram_router = APIRouter()


@ram_router.get(
    "/usage",
    response_model=List[GetRamResponseSchema],
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def get_ram(request: Request) -> List[GetRamResponseSchema]:
    """
    Route to get a list of RAM usage data.

    Args:
        request (Request): The incoming request.

    Returns:
        List[GetRamResponseSchema]: A list of RAM usage data as per the response model.
    """
    return await RamService().get_ram(request.app.state.monitortask)


@ram_router.get(
    "/info",
    response_model=GetRamInfoResponseSchema,
    responses={"400": {"model": ExceptionResponseSchema}},
)
async def get_ram_info(request: Request) -> GetRamInfoResponseSchema:
    """
    Route to get RAM information.

    Args:
        request (Request): The incoming request.

    Returns:
        GetRamInfoResponseSchema: RAM information details.
    """
    monitortask = request.app.state.monitortask
    return GetRamInfoResponseSchema(
        total=monitortask.total_ram,
        available=monitortask.available_ram,
        used=monitortask.used_ram,
        free=monitortask.free_ram
    )