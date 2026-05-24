from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .base import ConnectorBase


class LocalCalendarConnector(ConnectorBase):
    name = "local_calendar"

    def __init__(self, calendar_dir: Path):
        self.calendar_dir = Path(calendar_dir)
        self.calendar_dir.mkdir(parents=True, exist_ok=True)
        self.events_path = self.calendar_dir / "events.jsonl"

    def execute(self, operation: str, payload: dict[str, Any]) -> dict[str, Any]:
        if operation != "create_event":
            raise ValueError(f"unsupported local_calendar operation: {operation}")
        record = {"created_at": time.time(), **payload, "provider": "local_calendar_store"}
        with self.events_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        return {"events_path": str(self.events_path), "record": record}

