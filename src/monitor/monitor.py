"""This module defines a MonitorTask class for monitoring system metrics."""

import time
from typing import List
import psutil


class MonitorTask:
    """
    A class for monitoring system metrics including CPU and RAM usage.

    Attributes:
        interval (int): Time interval between metric updates in seconds
        num_cores (int): Number of CPU cores (physical)
        cpu_percent (List[float]): List of CPU usage percentages per core
        ram_percent (float): Total RAM usage percentage
        total_ram (float): Total RAM in MB
        available_ram (float): Available RAM in MB
        used_ram (float): Used RAM in MB
        free_ram (float): Free RAM in MB
    """

    interval: int
    num_cores: int
    cpu_percent: List[float]
    ram_percent: float
    total_ram: float
    available_ram: float
    used_ram: float
    free_ram: float

    def __init__(self) -> None:
        """Initialize the MonitorTask with current system metrics."""
        # Initialize monitoring interval
        self.interval = 3

        # Get CPU information
        self.num_cores = psutil.cpu_count(logical=False)
        self.cpu_percent = psutil.cpu_percent(percpu=True, interval=1)

        # Initialize RAM metrics
        self.ram_percent = 0.0
        self._update_ram_metrics()

    def _update_ram_metrics(self) -> None:
        """
        Update RAM-related metrics.
        
        Fetches current RAM usage statistics and updates instance attributes.
        All values are converted to MB for consistency.
        """
        ram = psutil.virtual_memory()
        self.ram_percent = ram.percent
        self.total_ram = ram.total / (1024 * 1024)
        self.available_ram = ram.available / (1024 * 1024)
        self.used_ram = ram.used / (1024 * 1024)
        self.free_ram = ram.free / (1024 * 1024)

    def monitor(self) -> None:
        """
        Continuously monitor system metrics.
        
        Runs in an infinite loop, updating CPU and RAM metrics at regular intervals.
        CPU percentages are collected with a small interval for accuracy.
        """
        while True:
            # Get per-CPU percentages with a small interval for accurate reading
            self.cpu_percent = psutil.cpu_percent(percpu=True, interval=0.1)
            
            # Update RAM metrics
            self._update_ram_metrics()
            
            # Sleep for the remaining time to maintain the desired interval
            time.sleep(max(0, self.interval - 0.1))  # Prevent negative sleep time