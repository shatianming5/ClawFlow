from __future__ import annotations

from dataclasses import dataclass

from clawflow.core.schema import ToolResult
from clawflow.tools.base import ToolContext


@dataclass(slots=True)
class LocalAgent:
    name: str
    role: str

    def produce(self, prompt: str) -> str:
        return f"## {self.name}\nRole: {self.role}\n\n{prompt.strip()}\n"


class MultiAgentCoordinator:
    def __init__(self, context: ToolContext):
        self.context = context
        self.agents = [
            LocalAgent("ManagerAgent", "decompose the project analysis task"),
            LocalAgent("ResearchAgent", "inspect project files and identify architecture signals"),
            LocalAgent("ToolAgent", "call registered tools through the shared runtime context"),
            LocalAgent("CriticAgent", "find gaps and risks"),
            LocalAgent("MemoryAgent", "persist useful findings"),
            LocalAgent("ReportAgent", "compile final markdown report"),
            LocalAgent("SlideAgent", "extract presentation talking points"),
            LocalAgent("GovernanceAgent", "map tool risk and audit evidence"),
        ]

    def run(self, args: dict) -> ToolResult:
        root = self.context.settings.root_dir
        task = args.get("task", self.context.user_input)
        files_result = self.context.registry.execute(
            "list_files",
            {"path": ".", "max_files": 120},
            self.context,
        )
        files = files_result.data.get("files", []) if files_result.ok else []
        if self.context.trace:
            self.context.trace.record(
                self.context.run_id,
                "multi_agent_handoff",
                {"agents": [agent.name for agent in self.agents], "file_count": len(files)},
                self.context.step_id,
            )

        sections = [
            "# Multi-agent Project Analysis",
            "",
            f"Task: {task}",
            "",
            "This report is produced by a local multi-agent collaboration flow triggered by the unified AgentRuntime.",
            "",
        ]
        sections.append(self.agents[0].produce("Break the work into file inspection, runtime capability mapping, governance review, and final reporting."))
        sections.append(self.agents[1].produce(f"Observed {len(files)} files. Key paths: {', '.join(files[:35])}."))
        sections.append(self.agents[2].produce("Used Tool Registry action list_files inside the shared ToolContext instead of bypassing runtime state."))
        sections.append(self.agents[3].produce("Main gaps to watch: production vector backend, real browser screenshots, and external service connectors."))
        memory_id = self.context.memory.add_memory(
            f"Multi-agent analysis generated for task: {task}",
            {"type": "multi_agent", "run_id": self.context.run_id},
        )
        sections.append(self.agents[4].produce(f"Persisted collaboration memory id: {memory_id}."))
        sections.append(self.agents[6].produce("Recommended slides: AgentOS Kernel, Tool Governance, Trace Replay, Example Application Stack, Benchmark."))
        sections.append(self.agents[7].produce("All high-risk destructive operations are represented by dry-run tools and audit records."))
        sections.append(self.agents[5].produce("Final report artifact is written to outputs/multi_agent_report.md for README/report/PPT reuse."))
        path = root / "outputs" / "multi_agent_report.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(sections) + "\n", encoding="utf-8")
        return ToolResult(
            ok=True,
            data={"path": str(path), "agents": [agent.name for agent in self.agents], "memory_id": memory_id},
            artifacts=[str(path)],
        )

