from __future__ import annotations

from dataclasses import dataclass

from clawflow.core.runtime import AgentRuntime


@dataclass(slots=True)
class ClawFlowApp:
    """Small developer-facing SDK wrapper for building Runtime-backed applications."""

    name: str
    task: str
    auto_approve: bool = True

    def run(self):
        return AgentRuntime().run(self.task, application=self.name, auto_approve=self.auto_approve)

