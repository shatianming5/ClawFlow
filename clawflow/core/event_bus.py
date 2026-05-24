from __future__ import annotations

import time
from collections import defaultdict
from typing import Any, Callable


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable[[dict[str, Any]], None]]] = defaultdict(list)
        self.history: list[dict[str, Any]] = []

    def subscribe(self, event_type: str, handler: Callable[[dict[str, Any]], None]) -> None:
        self._subscribers[event_type].append(handler)

    def publish(self, event_type: str, payload: dict[str, Any]) -> None:
        event = {"event_type": event_type, "payload": payload, "created_at": time.time()}
        self.history.append(event)
        for handler in self._subscribers.get(event_type, []):
            handler(event)

