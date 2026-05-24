from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from clawflow.config.settings import Settings
from clawflow.core.schema import ToolResult
from clawflow.memory.memory_store import MemoryStore


@dataclass(slots=True)
class ToolContext:
    settings: Settings
    memory: MemoryStore
    trace: Any = None
    run_id: str = ""
    step_id: str = ""
    user_input: str = ""
    registry: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseTool:
    name = "base"
    description = ""
    risk_level = "low"
    input_schema: dict[str, Any] = {}
    output_schema: dict[str, Any] = {}
    enabled = True

    def run(self, args: dict[str, Any], context: ToolContext) -> ToolResult:
        raise NotImplementedError

    def metadata(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "risk_level": self.risk_level,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "enabled": self.enabled,
        }

