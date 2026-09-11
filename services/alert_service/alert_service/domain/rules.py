"""Alert threshold rules."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AlertThresholds:
    temperature: float = 30.0
    humidity: float = 80.0
    voltage_high: float = 4.0
    voltage_low: float = 3.0
    ping: float = 500.0
    smoke: float = 1.0
    hysteresis_cycles: int = 2
    recovery_seconds: int = 180  # 3 minutos de recuperação (TFC sec 4.5)
