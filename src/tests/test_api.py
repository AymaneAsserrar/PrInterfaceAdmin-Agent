"""This module defines an exemple of test"""
import threading
from fastapi.testclient import TestClient
from server import app
from monitor import MonitorTask


class MonitorTaskFake(MonitorTask):
    """
    Monitor class to mock the real monitor
    Instead of using the real monitor that fetch data on the host
    we use a monitor that provide "fake" values to control the output
    and make deterministic test (deterministic = repeatable and known values)
    """
    interval: int = 0
    cpu_percent: list[float] = ["10", "12"]
    num_cores: int = 3

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
    assert response.status_code == 200
    assert response.json() == [{"id": 0, "usage": "10"}, {"id": 1, "usage": "12"}]
    # restore monitortask for next test
    app.state.monitortask = save_app


def test_get_cpu_core():
    response = client.get("/metrics/v1/cpu/core")
    # we can test types but not values because they will change at each test.
    assert response.status_code == 200
    assert isinstance(response.json()["number"], int)
