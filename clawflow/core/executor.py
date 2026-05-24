from __future__ import annotations

import time
from typing import Any

from clawflow.config.settings import Settings
from clawflow.core.schema import Plan, RunResult, ToolResult
from clawflow.governance.approval import ApprovalRequest, ApprovalStore
from clawflow.governance.policy import ToolPolicy
from clawflow.memory.memory_store import MemoryStore
from clawflow.observability.audit import AuditLog
from clawflow.observability.trace import TraceStore
from clawflow.tools.base import ToolContext
from clawflow.tools.registry import ToolRegistry
from clawflow.workflow.checkpoint import CheckpointStore
from clawflow.workflow.graph import StepGraph, WorkflowExporter


class Executor:
    def __init__(
        self,
        settings: Settings,
        registry: ToolRegistry,
        memory: MemoryStore,
        trace: TraceStore,
        audit: AuditLog,
        checkpoints: CheckpointStore,
        policy: ToolPolicy,
        approvals: ApprovalStore | None = None,
    ) -> None:
        self.settings = settings
        self.registry = registry
        self.memory = memory
        self.trace = trace
        self.audit = audit
        self.checkpoints = checkpoints
        self.policy = policy
        self.approvals = approvals

    def validate_plan(self, plan: Plan) -> list[str]:
        errors = []
        ids = {step.id for step in plan.steps}
        for step in plan.steps:
            if not self.registry.has(step.action):
                errors.append(f"{step.id}: missing tool {step.action}")
            for dep in step.depends_on:
                if dep not in ids:
                    errors.append(f"{step.id}: unknown dependency {dep}")
        return errors

    def execute(
        self,
        run_id: str,
        user_input: str,
        plan: Plan,
        auto_approve: bool = False,
        interactive: bool = False,
        initial_completed: set[str] | None = None,
        initial_artifacts: list[str] | None = None,
    ) -> RunResult:
        start = time.time()
        errors = self.validate_plan(plan)
        if errors:
            self.trace.record(run_id, "plan_validation_failed", {"errors": errors})
            return RunResult(run_id, "failed", "\n".join(errors), plan, error="\n".join(errors))

        graph = StepGraph.from_plan(plan)
        completed = set(initial_completed or set())
        artifacts = list(initial_artifacts or [])
        step_results: dict[str, Any] = {}
        for step_id in completed:
            graph.status[step_id] = "completed"
        self.trace.record(run_id, "workflow_graph_created", graph.to_dict())

        while True:
            ready = graph.ready_steps()
            if not ready:
                break
            for step in ready:
                if graph.status.get(step.id) == "completed":
                    continue
                graph.status[step.id] = "running"
                self.trace.record(run_id, "step_start", step.to_dict(), step.id)
                tool = self.registry.get(step.action)
                decision = self.policy.decide(tool.name, tool.risk_level, run_id, step.id)
                self.trace.record(run_id, "permission_decision", decision.to_dict(), step.id)
                self.audit.record(run_id, step.id, tool.name, tool.risk_level, decision.decision, decision.reason)

                if decision.decision == "deny":
                    graph.status[step.id] = "skipped"
                    self.trace.record(run_id, "step_skipped", {"reason": decision.reason}, step.id)
                    self._save_checkpoint(run_id, user_input, plan, graph, artifacts, step_results)
                    continue
                if decision.decision == "ask" and not auto_approve:
                    if interactive:
                        answer = input(f"Approve {tool.name} ({tool.risk_level})? [y/N] ").strip().lower()
                        if answer not in {"y", "yes"}:
                            graph.status[step.id] = "pending_approval"
                            self.trace.record(run_id, "approval_required", {"tool": tool.name, "risk": tool.risk_level}, step.id)
                            self.audit.record(run_id, step.id, tool.name, tool.risk_level, "pending", "human approval required")
                            self._create_approval(run_id, step.id, tool.name, tool.risk_level, "human approval required")
                            self._save_checkpoint(run_id, user_input, plan, graph, artifacts, step_results)
                            return self._result(run_id, "pending_approval", plan, artifacts, step_results, start)
                    else:
                        graph.status[step.id] = "pending_approval"
                        self.trace.record(run_id, "approval_required", {"tool": tool.name, "risk": tool.risk_level}, step.id)
                        self.audit.record(run_id, step.id, tool.name, tool.risk_level, "pending", "noninteractive approval required")
                        self._create_approval(run_id, step.id, tool.name, tool.risk_level, "noninteractive approval required")
                        self._save_checkpoint(run_id, user_input, plan, graph, artifacts, step_results)
                        return self._result(run_id, "pending_approval", plan, artifacts, step_results, start)
                elif decision.decision == "ask" and auto_approve:
                    self.trace.record(run_id, "approval_granted", {"tool": tool.name, "mode": "auto_approve"}, step.id)
                    self.audit.record(run_id, step.id, tool.name, tool.risk_level, "approved", "auto approval for local reproducible run")

                result = self._run_with_retry(run_id, step.id, tool.name, step.args, user_input)
                step_results[step.id] = result.to_dict()
                if result.artifacts:
                    artifacts.extend(result.artifacts)
                if result.ok:
                    graph.status[step.id] = "completed"
                    self.trace.record(run_id, "step_completed", result.to_dict(), step.id)
                else:
                    graph.status[step.id] = "failed"
                    self.trace.record(run_id, "step_failed", result.to_dict(), step.id)
                self._save_checkpoint(run_id, user_input, plan, graph, artifacts, step_results)

        failed = [sid for sid, status in graph.status.items() if status == "failed"]
        pending = [sid for sid, status in graph.status.items() if status == "pending_approval"]
        status = "failed" if failed else "pending_approval" if pending else "completed"
        WorkflowExporter.export_json(plan, self.settings.root_dir / "outputs" / f"workflow_{run_id}.json")
        final = self._result(run_id, status, plan, artifacts, step_results, start)
        self.trace.record(run_id, "reflection_summary", {"status": status, "artifacts": artifacts, "failed_steps": failed})
        return final

    def _create_approval(self, run_id: str, step_id: str, tool: str, risk_level: str, reason: str) -> None:
        if not self.approvals:
            return
        self.approvals.create(
            ApprovalRequest(
                run_id=run_id,
                step_id=step_id,
                tool=tool,
                risk_level=risk_level,
                reason=reason,
            )
        )

    def _run_with_retry(self, run_id: str, step_id: str, tool_name: str, args: dict[str, Any], user_input: str) -> ToolResult:
        context = ToolContext(
            settings=self.settings,
            memory=self.memory,
            trace=self.trace,
            run_id=run_id,
            step_id=step_id,
            user_input=user_input,
            registry=self.registry,
        )
        self.trace.record(run_id, "tool_call", {"tool": tool_name, "args": args}, step_id)
        try:
            result = self.registry.execute(tool_name, args, context)
            self.trace.record(run_id, "tool_result", result.to_dict(), step_id)
            return result
        except Exception as exc:
            result = ToolResult(ok=False, error=str(exc))
            self.trace.record(run_id, "error", {"tool": tool_name, "error": str(exc)}, step_id)
            return result

    def _save_checkpoint(
        self,
        run_id: str,
        user_input: str,
        plan: Plan,
        graph: StepGraph,
        artifacts: list[str],
        step_results: dict[str, Any],
    ) -> None:
        self.checkpoints.save(
            run_id,
            {
                "run_id": run_id,
                "user_input": user_input,
                "plan": plan.to_dict(),
                "graph": graph.to_dict(),
                "completed_steps": [sid for sid, status in graph.status.items() if status == "completed"],
                "artifacts": artifacts,
                "step_results": step_results,
                "updated_at": time.time(),
            },
        )
        self.trace.record(run_id, "checkpoint_saved", {"completed_steps": [sid for sid, status in graph.status.items() if status == "completed"]})

    def _result(
        self,
        run_id: str,
        status: str,
        plan: Plan,
        artifacts: list[str],
        step_results: dict[str, Any],
        start: float,
    ) -> RunResult:
        ok_steps = [res for res in step_results.values() if res.get("ok")]
        failed_steps = [res for res in step_results.values() if not res.get("ok")]
        final_answer = self._final_answer(status, artifacts, step_results)
        metrics = {
            "latency": round(time.time() - start, 4),
            "tool_calls": len(step_results),
            "successful_steps": len(ok_steps),
            "failed_steps": len(failed_steps),
            "artifact_count": len(artifacts),
            "estimated_tokens": max(20, len(final_answer) // 3),
            "estimated_cost": 0.0,
            "retry_count": 0,
        }
        return RunResult(run_id, status, final_answer, plan, artifacts, metrics)

    @staticmethod
    def _final_answer(status: str, artifacts: list[str], step_results: dict[str, Any]) -> str:
        lines = [f"Run status: {status}", ""]
        if artifacts:
            lines.append("Artifacts:")
            lines += [f"- {path}" for path in artifacts]
        else:
            lines.append("No artifacts generated.")
        lines.append("")
        lines.append("Step result summary:")
        for step_id, result in step_results.items():
            flag = "ok" if result.get("ok") else "error"
            lines.append(f"- {step_id}: {flag}")
        return "\n".join(lines)
