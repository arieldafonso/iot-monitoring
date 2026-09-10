"""Unit tests for PingResult entity."""

import pytest
from datetime import datetime
from ping_monitor.domain.entities import PingResult


class TestPingResult:
    def test_successful_result(self):
        result = PingResult(host="192.168.1.1", latency_ms=12.5, timestamp=datetime.utcnow())
        assert result.is_success is True
        assert result.latency_ms == 12.5

    def test_failed_result(self):
        result = PingResult.failed("192.168.1.1")
        assert result.is_success is False
        assert result.latency_ms is None
        assert result.host == "192.168.1.1"
