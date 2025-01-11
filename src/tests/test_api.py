"""
Test module for the monitoring API endpoints.

This module contains test cases for the monitoring API endpoints,
including CPU usage, RAM information, and log parsing functionality.
"""

import datetime
import threading
from typing import List

import pytest
from fastapi.testclient import TestClient

from monitor import MonitorTask
from monitor.monitor_log import parser_ligne, parser
from server import app


class MonitorTaskFake(MonitorTask):
    """
    Mock monitor class for testing purposes.

    Provides deterministic values for system metrics to enable
    reliable testing of the monitoring endpoints.

    Attributes:
        interval (int): Time interval between updates (set to 0 for testing)
        cpu_percent (List[float]): Mock CPU usage percentages
        num_cores (int): Number of CPU cores being monitored
        total_ram (float): Total RAM in MB
        available_ram (float): Available RAM in MB
        used_ram (float): Used RAM in MB
        free_ram (float): Free RAM in MB
    """

    def __init__(self):
        """Initialize the fake monitor with predetermined test values."""
        super().__init__()
        # Override the initialized values with test data
        self.interval = 0
        self.cpu_percent = [10.0, 12.0]
        self.num_cores = 2
        self.total_ram = 4000.0
        self.available_ram = 3000.0
        self.used_ram = 1000.0
        self.free_ram = 3000.0

    def monitor(self):
        """Override monitor method to prevent actual monitoring."""
        pass


# Initialize test client
client = TestClient(app)
thread = threading.Thread(target=app.state.monitortask.monitor, daemon=True)
thread.start()


def test_health():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200


def test_get_cpu_usage():
    """Test the CPU usage endpoint with mock data."""
    # Save original monitor task
    save_app = app.state.monitortask
    try:
        # Use fake monitor
        app.state.monitortask = MonitorTaskFake()
        response = client.get("/metrics/v1/cpu/usage")

        assert response.status_code == 200
        response_data = response.json()

        # Check the structure and content of the response
        assert "cpu_usage" in response_data, "Response should have 'cpu_usage' key"
        assert "average" in response_data, "Response should have 'average' key"

        # Check CPU usage data
        cpu_usage = response_data["cpu_usage"]
        assert len(cpu_usage) == 2, "Should have 2 CPU cores"

        # Check specific values
        expected_cpu_data = [
            {"core": 0, "usage": 10.0},
            {"core": 1, "usage": 12.0}
        ]
        assert cpu_usage == expected_cpu_data, (
            "CPU usage data doesn't match expected values"
        )

        # Check average
        assert response_data["average"] == 11.0, "Average CPU usage should be 11.0"

    finally:
        # Restore original monitor task
        app.state.monitortask = save_app


def test_get_ram_info():
    """Test the RAM information endpoint with mock data."""
    # Save original monitor task
    save_app = app.state.monitortask
    try:
        app.state.monitortask = MonitorTaskFake()
        response = client.get("/metrics/v1/ram/info")

        assert response.status_code == 200
        assert response.json() == {
            "total": 4000.0,
            "available": 3000.0,
            "used": 1000.0,
            "free": 3000.0
        }
    except Exception as e:
        pytest.fail(f"Test failed with error: {str(e)}")
    finally:
        # Restore original monitor task
        app.state.monitortask = save_app


def test_parser_ligne_simple():
    """Test parsing a single line of log data."""
    log = ('192.168.1.10 - - [01/Jan/2020:08:12:14 +0000] "GET / HTTP/1.1" '
           '200 1245 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"')
    resultat_attendu = [
        '192.168.1.10',
        '-',
        '200',
        '/',
        datetime.datetime(2020, 1, 1, 8, 12, 14)
    ]
    resultat = parser_ligne(log)
    assert resultat == resultat_attendu, f"Erreur : {resultat} != {resultat_attendu}"


def test_parser_simple(tmp_path):
    """Test parsing multiple lines of valid log data."""
    logs = [
        ('192.168.1.10 - - [01/Jan/2020:08:12:14 +0000] "GET / HTTP/1.1" '
         '200 1245 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"'),
        ('192.168.1.11 - - [01/Jan/2020:08:15:00 +0000] "POST /login HTTP/1.1" '
         '302 512 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"'),
        ('192.168.1.12 - - [01/Jan/2020:08:18:00 +0000] "GET /notfound HTTP/1.1" '
         '404 178 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"')
    ]
    log_file = tmp_path / "test_logs.log"
    log_file.write_text("\n".join(logs))

    resultat_attendu = [
        ['192.168.1.10', '-', '200', '/', datetime.datetime(2020, 1, 1, 8, 12, 14)],
        ['192.168.1.11', '-', '302', '/login', datetime.datetime(2020, 1, 1, 8, 15, 0)],
        ['192.168.1.12', '-', '404', '/notfound', datetime.datetime(2020, 1, 1, 8, 18, 0)]
    ]

    resultats = []
    with open(log_file, 'r', encoding='utf-8') as fichier:
        for ligne in fichier:
            resultats.append(parser_ligne(ligne.strip()))

    assert resultats == resultat_attendu, f"Erreur : {resultats} != {resultat_attendu}"


def test_parser_simple_invalid(tmp_path):
    """Test parsing invalid log data raises appropriate exceptions."""
    logs_invalides = [
        "192.168.1.10 - - [01/Jan/2020:08:12:14 +0000] GET / HTTP/1.1",
        "192.168.1.11 - - [01/Jan/2020:08:15:00 +0000] 302",
        "INVALID LOG LINE"
    ]
    log_file = tmp_path / "test_logs_invalid.log"
    log_file.write_text("\n".join(logs_invalides))

    with pytest.raises(Exception):
        parser(str(log_file))