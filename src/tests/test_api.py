"""
Test module for the monitoring API endpoints.

This module contains test cases for the monitoring API endpoints,
including CPU usage, RAM information, and log parsing functionality.
"""

import threading
from typing import List, Dict, Union


import pytest
from fastapi.testclient import TestClient

from monitor import MonitorTask
from monitor.monitor_log import parse_log_line, parse_log_file

from server import app

from pathlib import Path
from datetime import datetime


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

@pytest.fixture
def valid_log_line() -> str:
    return '192.168.1.1 - admin [10/Jan/2024:13:55:36 +0000] "GET /index.html HTTP/1.1" 200 2326'

@pytest.fixture
def valid_log_file(tmp_path) -> Path:
    content = """192.168.1.1 - admin [10/Jan/2024:13:55:36 +0000] "GET /index.html HTTP/1.1" 200 2326
192.168.1.2 - - [10/Jan/2024:13:56:36 +0000] "POST /api/data HTTP/1.1" 201 532
192.168.1.1 - admin [10/Jan/2024:13:57:36 +0000] "GET /about.html HTTP/1.1" 404 1234"""
    
    log_file = tmp_path / "test.log"
    log_file.write_text(content)
    return log_file

@pytest.fixture
def expected_parsed_line() -> Dict[str, Union[str, datetime]]:
    return {
        'remote_host': '192.168.1.1',
        'remote_user': 'admin',
        'status': '200',
        'request_url': '/index.html',
        'timestamp': datetime(2024, 1, 10, 13, 55, 36)
    }

class TestParseLogLine:
    def test_valid_line(self, valid_log_line, expected_parsed_line):
        """Test parsing a valid log line."""
        result = parse_log_line(valid_log_line)
        assert result == expected_parsed_line

    def test_empty_line(self):
        """Test parsing an empty line raises ValueError."""
        with pytest.raises(ValueError):
            parse_log_line("")

    def test_malformed_line(self):
        """Test parsing a malformed log line raises ValueError."""
        malformed_lines = [
            "Invalid log line",
            "192.168.1.1 - admin [invalid_date] GET /index.html HTTP/1.1 200",
            "192.168.1.1 - admin [10/Jan/2024:13:55:36 +0000] Invalid Request 200"
        ]
        for line in malformed_lines:
            with pytest.raises(ValueError):
                parse_log_line(line)

    def test_different_user_values(self):
        """Test parsing lines with different user values."""
        lines = {
            '192.168.1.1 - - [10/Jan/2024:13:55:36 +0000] "GET /index.html HTTP/1.1" 200 2326': '-',
            '192.168.1.1 - john [10/Jan/2024:13:55:36 +0000] "GET /index.html HTTP/1.1" 200 2326': 'john'
        }
        for line, expected_user in lines.items():
            result = parse_log_line(line)
            assert result['remote_user'] == expected_user

    def test_different_status_codes(self):
        """Test parsing lines with different HTTP status codes."""
        status_codes = ['200', '404', '500', '301']
        for status in status_codes:
            line = f'192.168.1.1 - admin [10/Jan/2024:13:55:36 +0000] "GET /index.html HTTP/1.1" {status} 2326'
            result = parse_log_line(line)
            assert result['status'] == status

class TestParseLogFile:
    def test_valid_file(self, valid_log_file):
        """Test parsing a valid log file."""
        results = parse_log_file(valid_log_file)
        assert len(results) == 3
        assert all(isinstance(r, dict) for r in results)
        assert all(isinstance(r['timestamp'], datetime) for r in results)

    def test_nonexistent_file(self):
        """Test parsing a non-existent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            parse_log_file(Path('nonexistent.log'))

    def test_empty_file(self, tmp_path):
        """Test parsing an empty file returns empty list."""
        empty_file = tmp_path / "empty.log"
        empty_file.write_text("")
        results = parse_log_file(empty_file)
        assert results == []

    def test_file_with_empty_lines(self, tmp_path):
        """Test parsing a file with empty lines."""
        content = """
192.168.1.1 - admin [10/Jan/2024:13:55:36 +0000] "GET /index.html HTTP/1.1" 200 2326

192.168.1.2 - - [10/Jan/2024:13:56:36 +0000] "POST /api/data HTTP/1.1" 201 532

"""
        log_file = tmp_path / "test_empty_lines.log"
        log_file.write_text(content)
        results = parse_log_file(log_file)
        assert len(results) == 2

    def test_file_with_invalid_lines(self, tmp_path):
        """Test parsing a file with some invalid lines raises ValueError."""
        content = """192.168.1.1 - admin [10/Jan/2024:13:55:36 +0000] "GET /index.html HTTP/1.1" 200 2326
Invalid Line
192.168.1.2 - - [10/Jan/2024:13:56:36 +0000] "POST /api/data HTTP/1.1" 201 532"""
        
        log_file = tmp_path / "test_invalid.log"
        log_file.write_text(content)
        with pytest.raises(ValueError):
            parse_log_file(log_file)

    @pytest.mark.parametrize("encoding", ["utf-8", "ascii", "latin-1"])
    def test_different_file_encodings(self, tmp_path, encoding):
        """Test parsing files with different encodings."""
        content = '192.168.1.1 - admin [10/Jan/2024:13:55:36 +0000] "GET /index.html HTTP/1.1" 200 2326'
        log_file = tmp_path / f"test_{encoding}.log"
        log_file.write_text(content, encoding=encoding)
        results = parse_log_file(log_file)
        assert len(results) == 1