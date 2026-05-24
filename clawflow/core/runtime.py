from __future__ import annotations

from pathlib import Path

from clawflow.config.settings import Settings, load_settings
from clawflow.core.executor import Executor
from clawflow.core.planner import Planner
from clawflow.core.prompts import PromptTemplateRegistry
from clawflow.core.schema import Plan, RunResult, new_id
from clawflow.governance.policy import PolicyStore, ToolPolicy
from clawflow.governance.approval import ApprovalStore
from clawflow.memory.memory_store import MemoryStore
from clawflow.observability.audit import AuditLog
from clawflow.observability.trace import TraceStore
from clawflow.tools.registry import ToolRegistry, create_default_registry
from clawflow.workflow.checkpoint import CheckpointStore


class AgentRuntime:
    """AgentOS Kernel facade: planning, execution, memory, trace, checkpoint, governance."""

    def __init__(self, settings: Settings | None = None, registry: ToolRegistry | None = None):
        self.settings = settings or load_settings()
        self.memory = MemoryStore(self.settings.database_path)
        self.trace = TraceStore(self.settings.database_path, self.settings.trace_path)
        self.audit = AuditLog(self.settings.database_path)
        self.approvals = ApprovalStore(self.settings.database_path)
        self.prompts = PromptTemplateRegistry(self.settings.database_path)
        self.checkpoints = CheckpointStore(self.settings.checkpoint_dir)
        self.registry = registry or create_default_registry(self.settings.root_dir)
        self.policy_store = PolicyStore(self.settings.database_path)
        self.policy = ToolPolicy(self.policy_store.get_policy(self.settings.policy))
        self.planner = Planner(self.settings, self.registry, self.memory)
        self.executor = Executor(
            self.settings,
            self.registry,
            self.memory,
            self.trace,
            self.audit,
            self.checkpoints,
            self.policy,
            self.approvals,
        )

    def run(
        self,
        user_input: str,
        application: str = "direct",
        run_id: str | None = None,
        auto_approve: bool = False,
        interactive: bool = False,
    ) -> RunResult:
        run_id = run_id or new_id("run")
        self.trace.start_run(run_id, user_input, application, status="planning")
        plan = self.planner.create_plan(user_input)
        self.trace.record(run_id, "plan_created", plan.to_dict())
        self.trace.update_run(run_id, status="running", plan=plan.to_dict())
        result = self.executor.execute(run_id, user_input, plan, auto_approve=auto_approve, interactive=interactive)
        self.trace.record(run_id, "final_answer", {"answer": result.final_answer, "status": result.status})
        self.trace.update_run(
            run_id,
            status=result.status,
            final_answer=result.final_answer,
            metrics=result.metrics,
            ended=result.status in {"completed", "failed"},
        )
        if result.status == "completed":
            self.memory.add_memory(
                f"Completed run {run_id} for application {application}: {user_input}",
                {"type": "run_summary", "run_id": run_id, "application": application, "artifacts": result.artifacts},
            )
            self.trace.record(run_id, "memory_update", {"application": application, "artifact_count": len(result.artifacts)})
        return result

    def resume(self, run_id: str, auto_approve: bool = False, interactive: bool = False) -> RunResult:
        state = self.checkpoints.load(run_id)
        if not state:
            raise ValueError(f"No checkpoint found for run_id={run_id}")
        plan = Plan.from_dict(state["plan"])
        completed = set(state.get("completed_steps", []))
        artifacts = list(state.get("artifacts", []))
        user_input = state.get("user_input", "")
        self.trace.record(run_id, "resume_started", {"completed_steps": list(completed)})
        self.trace.update_run(run_id, status="running")
        result = self.executor.execute(
            run_id,
            user_input,
            plan,
            auto_approve=auto_approve,
            interactive=interactive,
            initial_completed=completed,
            initial_artifacts=artifacts,
        )
        self.trace.record(run_id, "resume_finished", {"status": result.status})
        self.trace.update_run(run_id, status=result.status, final_answer=result.final_answer, metrics=result.metrics, ended=True)
        return result

    def approve(self, run_id: str) -> RunResult:
        request = self.approvals.decide(run_id, "approved")
        if not request:
            raise ValueError(f"No pending approval found for run_id={run_id}")
        self.trace.record(
            run_id,
            "human_approval_decision",
            {"decision": "approved", "step_id": request["step_id"], "tool": request["tool"]},
            request["step_id"],
        )
        self.audit.record(run_id, request["step_id"], request["tool"], request["risk_level"], "approved", "approved through ApprovalStore")
        return self.resume(run_id, auto_approve=True)

    def deny(self, run_id: str) -> RunResult:
        request = self.approvals.decide(run_id, "denied")
        if not request:
            raise ValueError(f"No pending approval found for run_id={run_id}")
        state = self.checkpoints.load(run_id) or {}
        plan = Plan.from_dict(state.get("plan", {"goal": "", "steps": []}))
        artifacts = list(state.get("artifacts", []))
        self.trace.record(
            run_id,
            "human_approval_decision",
            {"decision": "denied", "step_id": request["step_id"], "tool": request["tool"]},
            request["step_id"],
        )
        self.audit.record(run_id, request["step_id"], request["tool"], request["risk_level"], "denied", "denied through ApprovalStore")
        self.trace.update_run(run_id, status="failed", final_answer="Human approval denied; run stopped before high-risk tool execution.", ended=True)
        return RunResult(
            run_id=run_id,
            status="failed",
            final_answer="Human approval denied; run stopped before high-risk tool execution.",
            plan=plan,
            artifacts=artifacts,
            metrics={"approval_denied": 1, "tool_calls": 0},
            error="approval denied",
        )

    def replay(self, run_id: str) -> str:
        return self.trace.replay_text(run_id)

    def export_trace(self, run_id: str, output_path: str | Path | None = None) -> Path:
        output = Path(output_path) if output_path else self.settings.root_dir / "outputs" / f"trace_{run_id}.json"
        return self.trace.export_run(run_id, output)
