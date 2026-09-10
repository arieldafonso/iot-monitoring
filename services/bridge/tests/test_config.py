"""Unit tests for Bridge configuration."""

import pytest
from bridge.adapters.config import load_config


class TestConfigLoading:
    def test_load_config_defaults(self):
        config = load_config()
        assert config.mqtt.broker == "localhost"
        assert config.mqtt.port == 1883
        assert config.influxdb.host == "localhost"
        assert config.influxdb.port == 8086
        assert config.influxdb.database == "harryspace"
        assert config.log_level == "INFO"

    def test_load_config_from_env(self, monkeypatch):
        monkeypatch.setenv("MQTT_BROKER", "mqtt.example.com")
        monkeypatch.setenv("MQTT_PORT", "1883")
        monkeypatch.setenv("INFLUX_HOST", "influx.example.com")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        config = load_config()
        assert config.mqtt.broker == "mqtt.example.com"
        assert config.influxdb.host == "influx.example.com"
        assert config.log_level == "DEBUG"

    def test_load_config_partial_env(self, monkeypatch):
        monkeypatch.setenv("MQTT_BROKER", "custom-broker")
        config = load_config()
        assert config.mqtt.broker == "custom-broker"
        assert config.influxdb.host == "localhost"
