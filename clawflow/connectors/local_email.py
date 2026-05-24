from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .base import ConnectorBase


class LocalEmailConnector(ConnectorBase):
    name = "local_email"

    def __init__(self, outbox_dir: Path):
        self.outbox_dir = Path(outbox_dir)
        self.outbox_dir.mkdir(parents=True, exist_ok=True)
        self.outbox_path = self.outbox_dir / "outbox.jsonl"

    def execute(self, operation: str, payload: dict[str, Any]) -> dict[str, Any]:
        if operation != "send":
            raise ValueError(f"unsupported local_email operation: {operation}")
        record = {"created_at": time.time(), **payload, "provider": "local_email_outbox"}
        with self.outbox_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        return {"outbox_path": str(self.outbox_path), "record": record}

