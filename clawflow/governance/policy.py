from __future__ import annotations

import sqlite3
import time
from pathlib import Path
from typing import Any

from clawflow.core.schema import PermissionDecision


class ToolPolicy:
    def __init__(self, policy: dict[str, str] | None = None):
        self.policy = policy or {"low": "allow", "medium": "ask", "high": "ask"}

    def decide(self, tool_name: str, risk_level: str, run_id: str = "", step_id: str = "") -> PermissionDecision:
        decision = self.policy.get(risk_level, "deny")
        reason = f"default policy maps {risk_level} risk to {decision}"
        return PermissionDecision(
            tool=tool_name,
            risk_level=risk_level,  # type: ignore[arg-type]
            decision=decision,  # type: ignore[arg-type]
            reason=reason,
            run_id=run_id,
            step_id=step_id,
        )

    def export(self) -> dict[str, str]:
        return dict(self.policy)


class PolicyStore:
    """SQLite-backed editable policy overrides for runtime governance."""

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
                CREATE TABLE IF NOT EXISTS governance_policy (
                    risk_level TEXT PRIMARY KEY,
                    decision TEXT NOT NULL,
                    reason TEXT,
                    updated_at REAL NOT NULL
                )
                """
            )

    def get_policy(self, defaults: dict[str, str]) -> dict[str, str]:
        policy = dict(defaults)
        with self._connect() as conn:
            rows = conn.execute("SELECT risk_level, decision FROM governance_policy").fetchall()
        for row in rows:
            if row["risk_level"] in {"low", "medium", "high"} and row["decision"] in {"allow", "ask", "deny"}:
                policy[row["risk_level"]] = row["decision"]
        return policy

    def set_decision(self, risk_level: str, decision: str, reason: str = "") -> None:
        if risk_level not in {"low", "medium", "high"}:
            raise ValueError(f"invalid risk level: {risk_level}")
        if decision not in {"allow", "ask", "deny"}:
            raise ValueError(f"invalid decision: {decision}")
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO governance_policy(risk_level, decision, reason, updated_at)
                VALUES(?, ?, ?, ?)
                ON CONFLICT(risk_level) DO UPDATE SET
                    decision=excluded.decision,
                    reason=excluded.reason,
                    updated_at=excluded.updated_at
                """,
                (risk_level, decision, reason, time.time()),
            )

    def list(self, defaults: dict[str, str]) -> list[dict[str, Any]]:
        effective = self.get_policy(defaults)
        with self._connect() as conn:
            rows = {row["risk_level"]: dict(row) for row in conn.execute("SELECT * FROM governance_policy").fetchall()}
        result = []
        for risk in ["low", "medium", "high"]:
            row = rows.get(risk, {})
            result.append(
                {
                    "risk_level": risk,
                    "decision": effective[risk],
                    "source": "sqlite_override" if risk in rows else "config_default",
                    "reason": row.get("reason", ""),
                    "updated_at": row.get("updated_at"),
                }
            )
        return result
