from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any


class Scheduler:
    """A tiny local background task registry used to demonstrate AgentOS scheduling interfaces."""

    def __init__(self, database_path: Path):
        self.database_path = database_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS scheduled_tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    task_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    scheduled_at REAL NOT NULL,
                    created_at REAL NOT NULL
                )
                """
            )

    def add(self, name: str, task: dict[str, Any], scheduled_at: float | None = None) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO scheduled_tasks(name, task_json, status, scheduled_at, created_at) VALUES(?, ?, ?, ?, ?)",
                (name, json.dumps(task, ensure_ascii=False), "queued", scheduled_at or time.time(), time.time()),
            )
            return int(cur.lastrowid)

    def list(self, limit: int = 100) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM scheduled_tasks ORDER BY scheduled_at DESC LIMIT ?", (limit,)).fetchall()
        result = []
        for row in rows:
            data = dict(row)
            data["task"] = json.loads(data.pop("task_json"))
            result.append(data)
        return result

