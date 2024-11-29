"""
This module defines data transfer models for RAM-related response schemas.
"""
from pydantic import BaseModel


class GetRamResponseSchema(BaseModel):
    """
    Pydantic data model for the response schema representing RAM information.

    Attributes:
        id (int): The ID of the RAM data.
        usage (str): The RAM usage in string format.
    """

    id: int
    usage: str


class GetRamInfoResponseSchema(BaseModel):
    """
    Pydantic data model for the response schema representing RAM details.

    Attributes:
        total (float): Total RAM in the system.
        available (float): Available RAM.
        used (float): Used RAM.
        free (float): Free RAM.
    """

    total: float
    available: float
    used: float
    free: float