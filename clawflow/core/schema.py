from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

RiskLevel = Literal["low", "medium", "high"]
StepStatus = Literal["pending", "running", "completed", "failed", "skipped", "pending_approval"]
RunStatus = Literal["created", "planning", "running", "completed", "failed", "pending_approval"]


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


@dataclass(slots=True)
class PlanStep:
    id: str
    action: str
    args: dict[str, Any] = field(default_factory=dict)
    depends_on: list[str] = field(default_factory=list)
    retry: int = 0
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class Plan:
    goal: str
    steps: list[PlanStep]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"goal": self.goal, "steps": [s.to_dict() for s in self.steps], "metadata": self.metadata}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Plan":
        return cls(
            goal=data.get("goal", ""),
            steps=[PlanStep(**step) for step in data.get("steps", [])],
            metadata=data.get("metadata", {}),
        )


@dataclass(slots=True)
class ToolResult:
    ok: bool
    data: Any = None
    error: str = ""
    artifacts: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class PermissionDecision:
    tool: str
    risk_level: RiskLevel
    decision: Literal["allow", "deny", "ask", "approved", "pending"]
    reason: str
    run_id: str = ""
    step_id: str = ""
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class TraceEvent:
    run_id: str
    event_type: str
    payload: dict[str, Any]
    step_id: str = ""
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class RunResult:
    run_id: str
    status: RunStatus
    final_answer: str
    plan: Plan
    artifacts: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    error: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "status": self.status,
            "final_answer": self.final_answer,
            "plan": self.plan.to_dict(),
            "artifacts": self.artifacts,
            "metrics": self.metrics,
            "error": self.error,
        }

