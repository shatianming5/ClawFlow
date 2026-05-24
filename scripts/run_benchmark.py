from __future__ import annotations

import json
import statistics
import time
from pathlib import Path

from clawflow.config.settings import load_settings
from clawflow.core.runtime import AgentRuntime
from clawflow.observability.metrics import MetricsStore
from scripts._visual import draw_chart


DEFAULT_TASKS = [
    ("research", "请分析当前项目结构，生成项目摘要、README 摘要、技术报告大纲和 TODO 列表。"),
    ("personal", "请帮我制定明天的学习计划，并保存为 daily_plan.md，同时写入长期记忆。"),
    ("safe", "请删除 workspace 中的临时文件。"),
    ("multi-agent", "请让多个智能体协作完成一次项目分析。"),
    ("rag", "请根据 docs 中的项目文档回答 ClawFlow 的核心创新点。"),
    ("plugin", "请运行插件工具并展示插件注册能力。"),
]


def _p95(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, int(round(0.95 * (len(ordered) - 1))))
    return ordered[index]


def main() -> dict:
    settings = load_settings()
    runtime = AgentRuntime(settings)
    task_rows = []
    trace_before = {run["run_id"]: run for run in runtime.trace.list_runs(500)}
    for app, task in DEFAULT_TASKS:
        started = time.perf_counter()
        result = runtime.run(task, application=f"benchmark_{app}", auto_approve=True)
        latency = time.perf_counter() - started
        events = runtime.trace.get_events(result.run_id)
        approvals = [event for event in events if event["event_type"] in {"permission_decision", "approval_granted", "approval_required"}]
        task_rows.append(
            {
                "application": app,
                "task": task,
                "run_id": result.run_id,
                "status": result.status,
                "success": result.status == "completed",
                "latency": round(latency, 4),
                "tool_calls": result.metrics.get("tool_calls", 0),
                "failed_steps": result.metrics.get("failed_steps", 0),
                "approval_required_count": len([event for event in approvals if event["event_type"] == "approval_required"]),
                "trace_event_count": len(events),
                "retry_count": result.metrics.get("retry_count", 0),
                "artifact_count": len(result.artifacts),
            }
        )
    latencies = [row["latency"] for row in task_rows]
    success_count = sum(1 for row in task_rows if row["success"])
    result = {
        "total_tasks": len(task_rows),
        "success_tasks": success_count,
        "success_rate": round(success_count / max(1, len(task_rows)), 4),
        "average_latency": round(statistics.mean(latencies), 4) if latencies else 0,
        "p50_latency": round(statistics.median(latencies), 4) if latencies else 0,
        "p95_latency": round(_p95(latencies), 4),
        "average_tool_calls": round(statistics.mean([row["tool_calls"] for row in task_rows]), 4),
        "failed_steps": sum(row["failed_steps"] for row in task_rows),
        "approval_required_count": sum(row["approval_required_count"] for row in task_rows),
        "memory_hit_count": sum(mem["hit_count"] for mem in runtime.memory.list_memory(500)),
        "trace_event_count": sum(row["trace_event_count"] for row in task_rows),
        "retry_count": sum(row["retry_count"] for row in task_rows),
        "runtime_reuse_count": len(task_rows),
        "application_scenario_count": len(DEFAULT_TASKS),
        "tasks": task_rows,
    }
    Path("outputs").mkdir(exist_ok=True)
    Path("outputs/benchmark_results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    md = [
        "# Benchmark Results",
        "",
        f"- Total tasks: {result['total_tasks']}",
        f"- Success tasks: {result['success_tasks']}",
        f"- Success rate: {result['success_rate']}",
        f"- Average latency: {result['average_latency']}s",
        f"- p50 latency: {result['p50_latency']}s",
        f"- p95 latency: {result['p95_latency']}s",
        f"- Average tool calls: {result['average_tool_calls']}",
        f"- Trace event count: {result['trace_event_count']}",
        "",
        "| Application | Run ID | Status | Latency | Tool Calls | Trace Events |",
        "|---|---|---|---:|---:|---:|",
    ]
    for row in task_rows:
        md.append(f"| {row['application']} | `{row['run_id']}` | {row['status']} | {row['latency']} | {row['tool_calls']} | {row['trace_event_count']} |")
    Path("outputs/benchmark_results.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    labels = [row["application"] for row in task_rows]
    draw_chart("docs/assets/figures/benchmark_latency.png", "ClawFlow Benchmark Latency", labels, [row["latency"] for row in task_rows], "#0ea5e9")
    draw_chart("docs/assets/figures/benchmark_success_rate.png", "ClawFlow Success Rate", ["success", "failed"], [success_count, len(task_rows) - success_count], "#10b981")
    draw_chart("docs/assets/figures/benchmark_tool_calls.png", "Average Tool Calls by Application", labels, [row["tool_calls"] for row in task_rows], "#f59e0b")
    draw_chart("docs/assets/figures/benchmark_trace_events.png", "Trace Events by Application", labels, [row["trace_event_count"] for row in task_rows], "#8b5cf6")
    metrics = MetricsStore(settings.database_path)
    leaderboard = metrics.evaluation_leaderboard(Path("outputs/benchmark_results.json"))
    recovery = metrics.recovery_report(settings.checkpoint_dir)
    Path("outputs/evaluation_leaderboard.json").write_text(json.dumps(leaderboard, ensure_ascii=False, indent=2), encoding="utf-8")
    Path("outputs/failure_recovery_report.json").write_text(json.dumps(recovery, ensure_ascii=False, indent=2), encoding="utf-8")
    leaderboard_md = [
        "# Evaluation Leaderboard",
        "",
        "This leaderboard is computed from real benchmark task rows.",
        "",
        "| Rank | Application | Run ID | Score | Latency | Tool Calls | Trace Events |",
        "|---:|---|---|---:|---:|---:|---:|",
    ]
    for idx, row in enumerate(leaderboard.get("leaderboard", []), 1):
        leaderboard_md.append(
            f"| {idx} | {row['application']} | `{row['run_id']}` | {row['score']} | {row['latency']} | {row['tool_calls']} | {row['trace_event_count']} |"
        )
    Path("outputs/evaluation_leaderboard.md").write_text("\n".join(leaderboard_md) + "\n", encoding="utf-8")
    recovery_md = [
        "# Failure Recovery Report",
        "",
        "This report is computed from persisted runs, trace events, approval requests and checkpoint files.",
        "",
        "| Run ID | Status | Checkpoint | Recommended Action | Command |",
        "|---|---|---|---|---|",
    ]
    for row in recovery.get("recommendations", []):
        recovery_md.append(
            f"| `{row['run_id']}` | {row['status']} | {row['checkpoint_exists']} | {row['recommended_action']} | `{row['command']}` |"
        )
    Path("outputs/failure_recovery_report.md").write_text("\n".join(recovery_md) + "\n", encoding="utf-8")
    draw_chart(
        "docs/assets/figures/evaluation_leaderboard.png",
        "ClawFlow Evaluation Leaderboard",
        [row["application"] for row in leaderboard.get("leaderboard", [])],
        [float(row["score"]) for row in leaderboard.get("leaderboard", [])],
        "#14b8a6",
    )
    action_counts: dict[str, int] = {}
    for row in recovery.get("recommendations", []):
        action_counts[row["recommended_action"]] = action_counts.get(row["recommended_action"], 0) + 1
    draw_chart(
        "docs/assets/figures/failure_recovery_actions.png",
        "Failure Recovery Actions",
        list(action_counts.keys()) or ["none"],
        list(action_counts.values()) or [0],
        "#ef4444",
    )
    return result


if __name__ == "__main__":
    data = main()
    print(json.dumps(data, ensure_ascii=False, indent=2))
