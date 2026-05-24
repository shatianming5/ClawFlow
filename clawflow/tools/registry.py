from __future__ import annotations

from pathlib import Path
from typing import Iterable

from clawflow.tools.base import BaseTool, ToolContext


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def register_many(self, tools: Iterable[BaseTool]) -> None:
        for tool in tools:
            self.register(tool)

    def get(self, name: str) -> BaseTool:
        if name not in self._tools:
            raise KeyError(f"Tool not registered: {name}")
        return self._tools[name]

    def has(self, name: str) -> bool:
        return name in self._tools

    def list(self, include_disabled: bool = True) -> list[dict]:
        return [
            tool.metadata()
            for tool in sorted(self._tools.values(), key=lambda item: item.name)
            if include_disabled or tool.enabled
        ]

    def enable(self, name: str) -> None:
        self.get(name).enabled = True

    def disable(self, name: str) -> None:
        self.get(name).enabled = False

    def execute(self, name: str, args: dict, context: ToolContext):
        tool = self.get(name)
        if not tool.enabled:
            raise RuntimeError(f"Tool disabled: {name}")
        return tool.run(args, context)


def create_default_registry(root: Path | None = None) -> ToolRegistry:
    from clawflow.tools.file_tools import default_file_tools
    from clawflow.tools.local_calendar_tools import LocalCalendarStoreTool
    from clawflow.tools.local_email_tools import LocalEmailOutboxTool
    from clawflow.tools.plugin_loader import PluginLoader
    from clawflow.tools.rag_tools import RagAnswerTool, SearchKnowledgeBaseTool
    from clawflow.tools.report_tools import (
        BenchmarkTaskRunnerTool,
        CreateMarkdownReportTool,
        CreateRagNoteTool,
        CreateTodoTool,
        DeleteFileDryRunTool,
        GenerateDailyPlanTool,
        GenerateProjectSummaryTool,
        GenerateReportSectionTool,
        GenerateSlideOutlineTool,
        MultiAgentProjectAnalysisTool,
    )
    from clawflow.tools.shell_tools import ShellCommandTool

    registry = ToolRegistry()
    registry.register_many(default_file_tools())
    registry.register(ShellCommandTool())
    registry.register(LocalEmailOutboxTool())
    registry.register(LocalCalendarStoreTool())
    registry.register(CreateTodoTool())
    registry.register(CreateMarkdownReportTool())
    registry.register(GenerateDailyPlanTool())
    registry.register(GenerateProjectSummaryTool())
    registry.register(DeleteFileDryRunTool())
    registry.register(CreateRagNoteTool())
    registry.register(SearchKnowledgeBaseTool())
    registry.register(GenerateSlideOutlineTool())
    registry.register(GenerateReportSectionTool())
    registry.register(BenchmarkTaskRunnerTool())
    registry.register(MultiAgentProjectAnalysisTool())
    registry.register(RagAnswerTool())
    if root:
        PluginLoader(root / "clawflow" / "tools" / "plugin_manifest.json").load_into(registry)
    return registry

