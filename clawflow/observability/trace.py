from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any

from clawflow.core.schema import TraceEvent


class TraceStore:
    def __init__(self, database_path: Path, jsonl_path: Path):
        self.database_path = Path(database_path)
        self.jsonl_path = Path(jsonl_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    user_input TEXT NOT NULL,
                    application TEXT,
                    status TEXT NOT NULL,
                    started_at REAL NOT NULL,
                    ended_at REAL,
                    final_answer TEXT,
                    plan_json TEXT,
                    metrics_json TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS trace_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    step_id TEXT,
                    event_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at REAL NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_trace_run ON trace_events(run_id, id)")

    def start_run(self, run_id: str, user_input: str, application: str, status: str = "created") -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO runs(run_id, user_input, application, status, started_at, plan_json, metrics_json)
                VALUES(?, ?, ?, ?, ?, COALESCE((SELECT plan_json FROM runs WHERE run_id=?), ''), '{}')
                """,
                (run_id, user_input, application, status, time.time(), run_id),
            )
        self.record(run_id, "run_started", {"user_input": user_input, "application": application})

    def update_run(
        self,
        run_id: str,
        status: str | None = None,
        final_answer: str | None = None,
        plan: dict[str, Any] | None = None,
        metrics: dict[str, Any] | None = None,
        ended: bool = False,
    ) -> None:
        pieces: list[str] = []
        values: list[Any] = []
        if status is not None:
            pieces.append("status=?")
            values.append(status)
        if final_answer is not None:
            pieces.append("final_answer=?")
            values.append(final_answer)
        if plan is not None:
            pieces.append("plan_json=?")
            values.append(json.dumps(plan, ensure_ascii=False, indent=2))
        if metrics is not None:
            pieces.append("metrics_json=?")
            values.append(json.dumps(metrics, ensure_ascii=False, indent=2))
        if ended:
            pieces.append("ended_at=?")
            values.append(time.time())
        if not pieces:
            return
        values.append(run_id)
        with self._connect() as conn:
            conn.execute(f"UPDATE runs SET {', '.join(pieces)} WHERE run_id=?", values)

    def record(self, run_id: str, event_type: str, payload: dict[str, Any], step_id: str = "") -> None:
        event = TraceEvent(run_id=run_id, event_type=event_type, payload=payload, step_id=step_id)
        payload_json = json.dumps(payload, ensure_ascii=False, default=str)
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO trace_events(run_id, step_id, event_type, payload_json, created_at) VALUES(?, ?, ?, ?, ?)",
                (run_id, step_id, event_type, payload_json, event.created_at),
            )
        with self.jsonl_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event.to_dict(), ensure_ascii=False, default=str) + "\n")

    def list_runs(self, limit: int = 50) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM runs ORDER BY started_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(row) for row in rows]

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
        return dict(row) if row else None

    def get_events(self, run_id: str) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM trace_events WHERE run_id=? ORDER BY id ASC", (run_id,)
            ).fetchall()
        events: list[dict[str, Any]] = []
        for row in rows:
            data = dict(row)
            data["payload"] = json.loads(data.pop("payload_json"))
            events.append(data)
        return events

    def export_run(self, run_id: str, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        run = self.get_run(run_id) or {}
        events = self.get_events(run_id)
        output_path.write_text(
            json.dumps({"run": run, "events": events}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return output_path

    def replay_text(self, run_id: str) -> str:
        events = self.get_events(run_id)
        lines = [f"Trace replay for {run_id}", "=" * 72]
        for idx, event in enumerate(events, 1):
            step = f" [{event['step_id']}]" if event.get("step_id") else ""
            lines.append(f"{idx:02d}. {event['event_type']}{step}")
            payload = event.get("payload", {})
            if payload:
                summary = json.dumps(payload, ensure_ascii=False, default=str)
                lines.append(f"    {summary[:240]}")
        return "\n".join(lines)

