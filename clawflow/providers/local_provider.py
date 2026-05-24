from __future__ import annotations

import re
from typing import Any

from clawflow.core.schema import Plan, PlanStep
from clawflow.providers.base import PlanningProvider


class DeterministicLocalProvider(PlanningProvider):
    """Rule-based planner that changes plans based on task intent, files, tools, and memory context."""

    def create_plan(self, user_input: str, context: dict[str, Any]) -> Plan:
        text = user_input.lower()
        tools = set(context.get("tools", []))
        files = context.get("files", [])
        memory_hits = context.get("memory_hits", [])
        steps: list[PlanStep] = []

        def add(action: str, args: dict[str, Any] | None = None, desc: str = "", deps: list[str] | None = None) -> None:
            if action not in tools:
                return
            step_id = f"s{len(steps) + 1}"
            steps.append(PlanStep(id=step_id, action=action, args=args or {}, depends_on=deps or [], description=desc))

        add("list_files", {"path": ".", "max_files": 180}, "Inspect live workspace files")

        if self._is_multi_agent(text):
            add("multi_agent_project_analysis", {"task": user_input}, "Coordinate role-based agents", ["s1"])
            add("create_rag_note", {"text": f"Multi-agent project analysis requested: {user_input}", "metadata": {"type": "multi_agent"}}, "Persist collaboration memory", ["s2"])
        elif self._is_rag(text):
            search_path = "docs" if any(str(f).startswith("docs/") for f in files) else "."
            add("local_document_search", {"query": user_input, "path": search_path, "limit": 8}, "Retrieve project documentation", ["s1"])
            add("rag_answer", {"query": user_input, "path": "outputs/rag_answer.md"}, "Generate grounded RAG answer", ["s2"])
        elif self._is_delete(text):
            add("delete_file_dry_run", {"path": ".", "patterns": ["*.tmp", "*.temp", "*~", ".DS_Store"]}, "Dry-run high-risk deletion", ["s1"])
        elif self._is_personal(text):
            add("generate_daily_plan", {"task": user_input, "path": "outputs/daily_plan.md"}, "Create a persisted daily plan", ["s1"])
            if memory_hits:
                add("search_knowledge_base", {"query": user_input, "limit": 5}, "Retrieve relevant memory", ["s2"])
        elif self._is_plugin(text):
            add("plugin_workspace_stats", {}, "Run dynamically loaded plugin tool", ["s1"])
            add("plugin_echo", {"text": user_input}, "Demonstrate plugin execution", ["s2"])
        elif self._is_benchmark(text):
            add("benchmark_task_runner", {}, "Read benchmark result files", ["s1"])
        elif self._is_slide(text):
            add("generate_slide_outline", {"path": "slides/ppt_outline.md"}, "Generate slide outline", ["s1"])
        else:
            if "README.md" in files:
                add("summarize_file", {"path": "README.md"}, "Summarize README", ["s1"])
            add("generate_project_summary", {"task": user_input}, "Generate project summary and report outline", ["s1"])
            add("create_todo", {"task": user_input, "path": "outputs/TODO.md"}, "Create TODO list", [steps[-1].id] if steps else [])

        if len(steps) == 1:
            add("generate_project_summary", {"task": user_input}, "Fallback workspace summary", ["s1"])

        return Plan(
            goal=user_input,
            steps=steps,
            metadata={
                "provider": "deterministic_local",
                "tool_count": len(tools),
                "file_count": len(files),
                "memory_hits": len(memory_hits),
                "intent": self._intent(text),
            },
        )

    def _intent(self, text: str) -> str:
        for name, fn in [
            ("multi_agent", self._is_multi_agent),
            ("rag", self._is_rag),
            ("safe_delete", self._is_delete),
            ("personal", self._is_personal),
            ("plugin", self._is_plugin),
            ("benchmark", self._is_benchmark),
            ("slides", self._is_slide),
        ]:
            if fn(text):
                return name
        return "research"

    @staticmethod
    def _is_multi_agent(text: str) -> bool:
        return any(key in text for key in ["multi-agent", "multi agent", "多个智能体", "多智能体", "协作"])

    @staticmethod
    def _is_rag(text: str) -> bool:
        return any(key in text for key in ["rag", "知识库", "检索", "核心创新", "根据 docs", "根据文档"])

    @staticmethod
    def _is_delete(text: str) -> bool:
        return bool(re.search(r"删除|delete|remove|临时文件|temporary", text))

    @staticmethod
    def _is_personal(text: str) -> bool:
        return any(key in text for key in ["学习计划", "daily plan", "personal", "明天", "日程"])

    @staticmethod
    def _is_plugin(text: str) -> bool:
        return any(key in text for key in ["plugin", "插件", "marketplace"])

    @staticmethod
    def _is_benchmark(text: str) -> bool:
        return any(key in text for key in ["benchmark", "评测", "性能"])

    @staticmethod
    def _is_slide(text: str) -> bool:
        return any(key in text for key in ["ppt", "slide", "幻灯片"])
