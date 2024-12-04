"""This module defines an exemple of test"""
import threading
from fastapi.testclient import TestClient
from server import app
from monitor import MonitorTask
from typing import List


class MonitorTaskFake(MonitorTask):
    """
    Monitor class to mock the real monitor
    Instead of using the real monitor that fetch data on the host
    we use a monitor that provide "fake" values to control the output
    and make deterministic test (deterministic = repeatable and known values)
    """
    interval: int = 0
    cpu_percent: list[float] = ["10", "12"]
    total_ram = 4000.
    available_ram = 3000.
    used_ram = 1000.
    free_ram = 3000.      
    num_cores: int = 3

    def __init__(self): 
        None

    def monitor(self):
        pass

# Launching the real monitor for test involving the real monitor
client = TestClient(app)
thread = threading.Thread(target=app.state.monitortask.monitor, daemon=True)
thread.start()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200


def test_get_cpu_usage():
    # backup of the existing monitortask to restore it after the test
    save_app = app.state.monitortask
    # use fake monitor to have deterministic values
    app.state.monitortask = MonitorTaskFake()
    response = client.get("/metrics/v1/cpu/usage")
    print(app.state.monitortask.cpu_percent)
    assert response.status_code == 200
    assert response.json() == [{"id": 0, "usage": "10"}, {"id": 1, "usage": "12"}]
    # restore monitortask for next test
    app.state.monitortask = save_app





def test_get_ram_usage():
    # backup of the existing monitortask to restore it after the test
    save_app = app.state.monitortask
    # use fake monitor to have deterministic values
    app.state.monitortask = MonitorTaskFake()
    response = client.get("/metrics/v1/ram/info")
    assert response.status_code == 200
    assert response.json() == {"total" : 4000., "available": 3000. , "used": 1000., "free": 3000.}
    # restore monitortask for next test
    app.state.monitortask = save_app