from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class ApprovalRequest:
    run_id: str
    step_id: str
    tool: str
    risk_level: str
    reason: str
    status: str = "pending"


class ApprovalStore:
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
                CREATE TABLE IF NOT EXISTS approval_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    step_id TEXT NOT NULL,
                    tool TEXT NOT NULL,
                    risk_level TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    decided_at REAL,
                    UNIQUE(run_id, step_id)
                )
                """
            )

    def create(self, request: ApprovalRequest) -> int:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO approval_requests(run_id, step_id, tool, risk_level, reason, status, created_at)
                VALUES(?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(run_id, step_id) DO UPDATE SET
                    tool=excluded.tool,
                    risk_level=excluded.risk_level,
                    reason=excluded.reason,
                    status='pending',
                    decided_at=NULL
                """,
                (
                    request.run_id,
                    request.step_id,
                    request.tool,
                    request.risk_level,
                    request.reason,
                    request.status,
                    time.time(),
                ),
            )
            row = conn.execute(
                "SELECT id FROM approval_requests WHERE run_id=? AND step_id=?",
                (request.run_id, request.step_id),
            ).fetchone()
            return int(row["id"])

    def decide(self, run_id: str, decision: str, step_id: str | None = None) -> dict[str, Any] | None:
        with self._connect() as conn:
            if step_id:
                row = conn.execute(
                    "SELECT * FROM approval_requests WHERE run_id=? AND step_id=? ORDER BY id DESC LIMIT 1",
                    (run_id, step_id),
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT * FROM approval_requests WHERE run_id=? AND status='pending' ORDER BY id DESC LIMIT 1",
                    (run_id,),
                ).fetchone()
            if not row:
                return None
            conn.execute(
                "UPDATE approval_requests SET status=?, decided_at=? WHERE id=?",
                (decision, time.time(), row["id"]),
            )
            data = dict(row)
            data["status"] = decision
            data["decided_at"] = time.time()
            return data

    def list(self, status: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        query = "SELECT * FROM approval_requests"
        values: list[Any] = []
        if status:
            query += " WHERE status=?"
            values.append(status)
        query += " ORDER BY id DESC LIMIT ?"
        values.append(limit)
        with self._connect() as conn:
            rows = conn.execute(query, values).fetchall()
        return [dict(row) for row in rows]

    def get_pending(self, run_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM approval_requests WHERE run_id=? AND status='pending' ORDER BY id DESC LIMIT 1",
                (run_id,),
            ).fetchone()
        return dict(row) if row else None
