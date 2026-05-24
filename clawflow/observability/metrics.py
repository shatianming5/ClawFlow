from __future__ import annotations

import sqlite3
import json
from pathlib import Path
from typing import Any


class MetricsStore:
    """Read aggregate runtime metrics from persisted run and trace tables."""

    def __init__(self, database_path: Path):
        self.database_path = Path(database_path)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        return conn

    def summary(self) -> dict:
        with self._connect() as conn:
            runs = conn.execute("SELECT status, metrics_json FROM runs").fetchall()
            events = conn.execute("SELECT event_type, COUNT(*) AS count FROM trace_events GROUP BY event_type").fetchall()
        total = len(runs)
        completed = sum(1 for row in runs if row["status"] == "completed")
        pending = sum(1 for row in runs if row["status"] == "pending_approval")
        failed = sum(1 for row in runs if row["status"] == "failed")
        return {
            "total_runs": total,
            "completed_runs": completed,
            "pending_approval_runs": pending,
            "failed_runs": failed,
            "success_rate": round(completed / total, 4) if total else 0,
            "event_counts": {row["event_type"]: row["count"] for row in events},
        }

    def cost_summary(self) -> dict[str, Any]:
        with self._connect() as conn:
            rows = conn.execute("SELECT run_id, application, status, metrics_json FROM runs ORDER BY started_at DESC").fetchall()
        runs = []
        total_tokens = 0
        total_cost = 0.0
        for row in rows:
            try:
                metrics = json.loads(row["metrics_json"] or "{}")
            except json.JSONDecodeError:
                metrics = {}
            tokens = int(metrics.get("estimated_tokens", 0) or 0)
            cost = float(metrics.get("estimated_cost", 0.0) or 0.0)
            total_tokens += tokens
            total_cost += cost
            runs.append(
                {
                    "run_id": row["run_id"],
                    "application": row["application"],
                    "status": row["status"],
                    "estimated_tokens": tokens,
                    "estimated_cost": cost,
                    "tool_calls": metrics.get("tool_calls", 0),
                    "latency": metrics.get("latency", 0),
                }
            )
        return {"total_estimated_tokens": total_tokens, "total_estimated_cost": round(total_cost, 6), "runs": runs[:100]}

    def failure_analysis(self) -> dict[str, Any]:
        with self._connect() as conn:
            failed_runs = conn.execute(
                "SELECT run_id, application, status, user_input, final_answer FROM runs WHERE status IN ('failed', 'pending_approval') ORDER BY started_at DESC LIMIT 100"
            ).fetchall()
            errors = conn.execute(
                "SELECT run_id, step_id, payload_json, created_at FROM trace_events WHERE event_type IN ('error', 'step_failed', 'approval_required') ORDER BY id DESC LIMIT 100"
            ).fetchall()
        return {
            "failed_or_pending_runs": [dict(row) for row in failed_runs],
            "recent_failure_events": [
                {
                    "run_id": row["run_id"],
                    "step_id": row["step_id"],
                    "payload": json.loads(row["payload_json"]),
                    "created_at": row["created_at"],
                }
                for row in errors
            ],
        }

    def tool_usage(self) -> dict[str, Any]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT payload_json FROM trace_events WHERE event_type='tool_call'"
            ).fetchall()
        counts: dict[str, int] = {}
        for row in rows:
            try:
                payload = json.loads(row["payload_json"])
            except json.JSONDecodeError:
                continue
            tool = payload.get("tool", "unknown")
            counts[tool] = counts.get(tool, 0) + 1
        ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        return {"total_tool_calls": sum(counts.values()), "tools": [{"tool": name, "count": count} for name, count in ordered]}

    def evaluation_leaderboard(self, benchmark_path: Path | None = None) -> dict[str, Any]:
        path = benchmark_path or self.database_path.parent / "benchmark_results.json"
        if not path.exists():
            return {"leaderboard": [], "source": str(path), "status": "missing"}
        benchmark = json.loads(path.read_text(encoding="utf-8"))
        rows = []
        for task in benchmark.get("tasks", []):
            latency = float(task.get("latency", 0) or 0)
            trace_events = int(task.get("trace_event_count", 0) or 0)
            tool_calls = int(task.get("tool_calls", 0) or 0)
            artifact_count = int(task.get("artifact_count", 0) or 0)
            success_score = 40 if task.get("success") else 0
            latency_score = max(0, 20 - latency * 20)
            trace_score = min(15, trace_events / 2)
            tool_score = min(15, tool_calls * 4)
            artifact_score = min(10, artifact_count * 3)
            governance_bonus = 5 if task.get("application") in {"safe", "plugin"} else 0
            score = round(success_score + latency_score + trace_score + tool_score + artifact_score + governance_bonus, 2)
            rows.append(
                {
                    "application": task.get("application"),
                    "run_id": task.get("run_id"),
                    "status": task.get("status"),
                    "score": score,
                    "latency": latency,
                    "tool_calls": tool_calls,
                    "trace_event_count": trace_events,
                    "artifact_count": artifact_count,
                    "rationale": "success + latency + trace richness + tool reuse + artifacts + governance bonus",
                }
            )
        rows.sort(key=lambda item: (-item["score"], item["latency"], item["application"] or ""))
        return {
            "source": str(path),
            "status": "ok",
            "leaderboard": rows,
            "metric": "ClawFlow local infrastructure evaluation score",
        }

    def recovery_report(self, checkpoint_dir: Path | None = None) -> dict[str, Any]:
        checkpoint_root = checkpoint_dir or self.database_path.parent / "checkpoints"
        failures = self.failure_analysis()
        pending_or_failed = failures["failed_or_pending_runs"]
        approval_rows = []
        with self._connect() as conn:
            try:
                approval_rows = [dict(row) for row in conn.execute("SELECT * FROM approval_requests ORDER BY id DESC").fetchall()]
            except sqlite3.OperationalError:
                approval_rows = []
        approvals_by_run = {row["run_id"]: row for row in approval_rows}
        recommendations = []
        for run in pending_or_failed:
            run_id = run["run_id"]
            checkpoint_path = checkpoint_root / f"{run_id}.json"
            checkpoint = {}
            if checkpoint_path.exists():
                try:
                    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    checkpoint = {}
            approval = approvals_by_run.get(run_id)
            if run["status"] == "pending_approval" and approval and approval.get("status") == "pending":
                action = "approve_or_deny"
                command = f"clawflow approvals approve {run_id}"
                reason = "Run is paused at a human-in-the-loop approval boundary."
            elif run["status"] == "pending_approval":
                action = "inspect_checkpoint"
                command = f"clawflow trace replay {run_id}"
                reason = "Run is pending but no active approval row was found."
            else:
                action = "replay_and_rerun"
                command = f"clawflow trace replay {run_id}"
                reason = "Run failed; inspect trace and checkpoint before rerun."
            recommendations.append(
                {
                    "run_id": run_id,
                    "application": run.get("application"),
                    "status": run["status"],
                    "checkpoint_exists": checkpoint_path.exists(),
                    "completed_steps": checkpoint.get("completed_steps", []),
                    "approval_status": approval.get("status") if approval else None,
                    "recommended_action": action,
                    "command": command,
                    "reason": reason,
                }
            )
        return {
            "status": "ok",
            "recommendations": recommendations,
            "failure_event_count": len(failures["recent_failure_events"]),
            "checkpoint_dir": str(checkpoint_root),
        }
