"""Subprocess-based ping adapter."""

import logging
import re
import subprocess
from datetime import datetime

from ..domain.entities import PingResult
from ..ports.ping_gateway import PingGateway

logger = logging.getLogger(__name__)


class SubprocessPingGateway(PingGateway):
    def ping(self, host: str) -> PingResult:
        try:
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "2", host],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                logger.debug("Ping to %s failed (return code: %s)", host, result.returncode)
                return PingResult.failed(host)

            match = re.search(r"time[=<]([\d.]+)", result.stdout)
            if match:
                latency = float(match.group(1))
                logger.debug("Ping %s: %.2fms", host, latency)
                return PingResult(host=host, latency_ms=latency, timestamp=datetime.utcnow())

            logger.warning("Could not parse ping output for %s", host)
            return PingResult.failed(host)

        except subprocess.TimeoutExpired:
            logger.warning("Ping to %s timed out", host)
            return PingResult.failed(host)
        except FileNotFoundError:
            logger.error("ping command not found (is iputils-ping installed?)")
            return PingResult.failed(host)
        except Exception as exc:
            logger.exception("Error pinging %s: %s", host, exc)
            return PingResult.failed(host)
