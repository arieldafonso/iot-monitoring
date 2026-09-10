"""Unit tests for MonitorPing use case."""

import pytest
from unittest.mock import MagicMock
from datetime import datetime
from ping_monitor.domain.entities import PingResult
from ping_monitor.use_cases.monitor_ping import MonitorPing


@pytest.fixture
def mock_ping_gateway():
    gw = MagicMock()
    gw.ping.return_value = PingResult(host="192.168.1.1", latency_ms=12.5, timestamp=datetime.utcnow())
    return gw


@pytest.fixture
def mock_publisher():
    pub = MagicMock()
    pub.publish.return_value = True
    return pub


@pytest.fixture
def use_case(mock_ping_gateway, mock_publisher):
    return MonitorPing(mock_ping_gateway, mock_publisher)


class TestMonitorPing:
    def test_successful_ping(self, use_case, mock_publisher):
        result = use_case.execute("192.168.1.1")
        assert result.is_success is True
        mock_publisher.publish.assert_called_once_with(12.5)

    def test_failed_ping(self, use_case, mock_ping_gateway, mock_publisher):
        mock_ping_gateway.ping.return_value = PingResult.failed("192.168.1.1")
        result = use_case.execute("192.168.1.1")
        assert result.is_success is False
        mock_publisher.publish.assert_called_once_with(-1.0)
