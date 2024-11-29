"""
This module defines a data model for RAM information.
"""
from pydantic import BaseModel


# RAM data model
class Ram(BaseModel):
    """
    Pydantic data model for representing RAM information.

    Attributes:
        id (int): The ID of the RAM data.
        usage (str): The RAM usage in string format.
    """

    id: int
    usage: str