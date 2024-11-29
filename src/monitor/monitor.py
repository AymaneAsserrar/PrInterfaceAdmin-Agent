"""This module defines a `MonitorTask` class for monitoring metrics on a host."""
import time
import psutil


class MonitorTask:
    """A class for monitoring metrics."""

    interval: int
    cpu_percent: list[float]
    num_cores: int
    ram_percent: float
    total_ram: float
    available_ram: float
    used_ram: float
    free_ram: float

    def __init__(self) -> None:
        """
        Initialize the MonitorTask class.
        Add initialization tasks here like checks
        The monitoring interval is 3 seconds.
        """
        self.interval = 3
        self.num_cores = psutil.cpu_count(logical=False)
        self.cpu_percent = [0] * self.num_cores
        self.ram_percent = 0
        self._update_ram_metrics()
        self.total_ram = 0.
        self.used_ram = 0.
        self.available_ram = 0.
        self.free_ram = 0.

    def _update_ram_metrics(self):
        """Update RAM-related metrics."""
        ram = psutil.virtual_memory()
        self.ram_percent = ram.percent
        self.total_ram = ram.total / (1024 * 1024)  # Convert to MB
        self.available_ram = ram.available / (1024 * 1024)
        self.used_ram = ram.used / (1024 * 1024)
        self.free_ram = ram.free / (1024 * 1024)

    def monitor(self):
        """Continuously monitor and store the result in an attribute."""
        while True:
            self.cpu_percent = psutil.cpu_percent(percpu=True)
            self._update_ram_metrics()
            time.sleep(self.interval)

    def __str__(self) -> str:
        return f"MonitorTask(interval = {self.interval})"