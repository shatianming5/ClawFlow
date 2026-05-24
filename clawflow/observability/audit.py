from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any


class AuditLog:
    def __init__(self, database_path: Path):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT,
                    step_id TEXT,
                    tool TEXT,
                    risk_level TEXT,
                    decision TEXT,
                    reason TEXT,
                    metadata_json TEXT,
                    created_at REAL NOT NULL
                )
                """
            )

    def record(
        self,
        run_id: str,
        step_id: str,
        tool: str,
        risk_level: str,
        decision: str,
        reason: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO audit_events(run_id, step_id, tool, risk_level, decision, reason, metadata_json, created_at)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    step_id,
                    tool,
                    risk_level,
                    decision,
                    reason,
                    json.dumps(metadata or {}, ensure_ascii=False),
                    time.time(),
                ),
            )

    def list_events(self, limit: int = 100) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM audit_events ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        events = []
        for row in rows:
            data = dict(row)
            data["metadata"] = json.loads(data.pop("metadata_json") or "{}")
            events.append(data)
        return events

