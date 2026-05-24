from __future__ import annotations

from pathlib import Path

from clawflow.config.settings import Settings
from clawflow.core.schema import Plan
from clawflow.memory.memory_store import MemoryStore
from clawflow.providers.local_provider import DeterministicLocalProvider
from clawflow.providers.openai_compatible import OpenAICompatibleProvider
from clawflow.tools.registry import ToolRegistry


class Planner:
    def __init__(self, settings: Settings, registry: ToolRegistry, memory: MemoryStore):
        self.settings = settings
        self.registry = registry
        self.memory = memory
        if settings.llm_mode == "llm":
            self.provider = OpenAICompatibleProvider(settings.openai_api_key, settings.openai_base_url, settings.openai_model)
        else:
            self.provider = DeterministicLocalProvider()

    def create_plan(self, user_input: str) -> Plan:
        files = self._sample_files(self.settings.root_dir)
        memory_hits = self.memory.search_memory(user_input, limit=5)
        context = {
            "tools": [tool["name"] for tool in self.registry.list(include_disabled=False)],
            "files": files,
            "memory_hits": memory_hits,
        }
        return self.provider.create_plan(user_input, context)

    @staticmethod
    def _sample_files(root: Path, limit: int = 300) -> list[str]:
        ignore = {".git", ".venv", "__pycache__", ".pytest_cache", "node_modules"}
        files: list[str] = []
        for path in root.rglob("*"):
            if any(part in ignore for part in path.parts):
                continue
            if path.is_file():
                files.append(str(path.relative_to(root)))
                if len(files) >= limit:
                    break
        return files

