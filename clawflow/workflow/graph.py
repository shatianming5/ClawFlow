from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from clawflow.core.schema import Plan, PlanStep


@dataclass
class StepGraph:
    steps: dict[str, PlanStep] = field(default_factory=dict)
    status: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_plan(cls, plan: Plan) -> "StepGraph":
        graph = cls()
        for step in plan.steps:
            graph.steps[step.id] = step
            graph.status[step.id] = "pending"
        return graph

    def ready_steps(self) -> list[PlanStep]:
        ready: list[PlanStep] = []
        for step_id, step in self.steps.items():
            if self.status.get(step_id) != "pending":
                continue
            if all(self.status.get(dep) == "completed" for dep in step.depends_on):
                ready.append(step)
        return ready

    def to_dict(self) -> dict[str, Any]:
        return {
            "steps": [step.to_dict() for step in self.steps.values()],
            "status": self.status,
            "edges": [{"from": dep, "to": step.id} for step in self.steps.values() for dep in step.depends_on],
        }


class WorkflowExporter:
    @staticmethod
    def export_json(plan: Plan, output_path: Path) -> Path:
        graph = StepGraph.from_plan(plan)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(graph.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return output_path

    @staticmethod
    def export_mermaid(plan: Plan, output_path: Path) -> Path:
        lines = ["graph TD"]
        for step in plan.steps:
            label = f"{step.id}[{step.action}]"
            lines.append(f"  {label}")
            for dep in step.depends_on:
                lines.append(f"  {dep} --> {step.id}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("\n".join(lines), encoding="utf-8")
        return output_path

