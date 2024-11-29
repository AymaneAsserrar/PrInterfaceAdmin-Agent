"""
This module defines a service class for fetching RAM values from a monitoring task.
"""
from typing import List
from domain.models import Ram
from monitor import MonitorTask


class RamService:
    """
    Service class to fetch RAM values from a monitoring task.
    """

    def __init__(self):
        ...

    async def get_ram(self, monitor_task: MonitorTask) -> List[Ram]:
        """
        Get RAM values from the provided monitoring task and return them as a list of Ram objects.

        Args:
            monitor_task (MonitorTask): The monitoring task to fetch RAM data from.

        Returns:
            List[Ram]: A list of Ram objects containing RAM values.
        """
        ramlist = []
        ramlist.append(Ram(id=0, usage=str(monitor_task.ram_percent)))
        return ramlist

    def __str__(self):
        return self.__class__.__name__