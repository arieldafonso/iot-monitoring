"""Domain entity for heartbeat tracking."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class HeartbeatStatus:
    room_id: str
    last_seen: datetime
    is_online: bool = True
    missed_cycles: int = 0
