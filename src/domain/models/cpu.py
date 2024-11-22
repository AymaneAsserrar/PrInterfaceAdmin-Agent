"""
This module defines a data model for CPU information.
"""
from pydantic import BaseModel


# CPU data model
class Cpu(BaseModel):
    """
    Pydantic data model for representing CPU information.

    Attributes:
        id (int): The ID of the CPU data.
        usage (str): The CPU usage in string format.
    """

    id: int
    usage: str
