"""Use case for monitoring node heartbeats."""

import logging
from datetime import datetime, timedelta
from typing import Callable, Dict, Optional

from ..domain.entities import HeartbeatStatus

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT_SECONDS = 180


class MonitorHeartbeat:
    def __init__(
        self,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        on_node_lost: Optional[Callable[[str], None]] = None,
        on_node_recovered: Optional[Callable[[str], None]] = None,
    ) -> None:
        self._timeout = timedelta(seconds=timeout_seconds)
        self._nodes: Dict[str, HeartbeatStatus] = {}
        self._on_node_lost = on_node_lost
        self._on_node_recovered = on_node_recovered

    def record_heartbeat(self, room_id: str) -> None:
        now = datetime.utcnow()
        node = self._nodes.get(room_id)

        if node is None:
            self._nodes[room_id] = HeartbeatStatus(room_id=room_id, last_seen=now)
            logger.info("Node %s registered (first heartbeat)", room_id)
            return

        was_offline = not node.is_online
        node.last_seen = now
        node.missed_cycles = 0

        if was_offline:
            node.is_online = True
            logger.info("Node %s recovered (back online)", room_id)
            if self._on_node_recovered:
                self._on_node_recovered(room_id)

    def check_timeouts(self) -> None:
        now = datetime.utcnow()
        for room_id, node in self._nodes.items():
            if node.is_online and (now - node.last_seen) > self._timeout:
                node.is_online = False
                node.missed_cycles += 1
                logger.critical(
                    "Node %s OFFLINE — no heartbeat for %s seconds",
                    room_id, int(self._timeout.total_seconds()),
                )
                if self._on_node_lost:
                    self._on_node_lost(room_id)
            elif not node.is_online:
                node.missed_cycles += 1

    def get_status(self, room_id: str) -> Optional[HeartbeatStatus]:
        return self._nodes.get(room_id)

    def get_all_statuses(self) -> Dict[str, HeartbeatStatus]:
        return dict(self._nodes)
