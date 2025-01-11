"""This module defines a `MonitorTask` class for monitoring metrics on a host."""
import time
import psutil
from typing import List

class MonitorTask:
    """A class for monitoring metrics."""

    def __init__(self) -> None:
        """Initialize the MonitorTask class."""
        self.interval = 3
        self.num_cores = psutil.cpu_count(logical=False)
        # Initialize with actual CPU percentages instead of zeros
        self.cpu_percent = psutil.cpu_percent(percpu=True, interval=1)
        self.ram_percent = 0
        
        # Initialize RAM values
        ram = psutil.virtual_memory()
        self.total_ram = ram.total / (1024 * 1024)
        self.available_ram = ram.available / (1024 * 1024)
        self.used_ram = ram.used / (1024 * 1024)
        self.free_ram = ram.free / (1024 * 1024)

    def _update_ram_metrics(self):
        """Update RAM-related metrics."""
        ram = psutil.virtual_memory()
        self.ram_percent = ram.percent
        self.total_ram = ram.total / (1024 * 1024)
        self.available_ram = ram.available / (1024 * 1024)
        self.used_ram = ram.used / (1024 * 1024)
        self.free_ram = ram.free / (1024 * 1024)

    def monitor(self):
        """Continuously monitor and store the result in an attribute."""
        while True:
            # Get per-CPU percentages with a small interval for accurate first reading
            self.cpu_percent = psutil.cpu_percent(percpu=True, interval=0.1)
            self._update_ram_metrics()
            time.sleep(self.interval - 0.1)  # Adjust sleep time to account for the interval