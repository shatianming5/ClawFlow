from __future__ import annotations

from pathlib import Path
from typing import Any

from .base import ConnectorBase


class LocalSearchConnector(ConnectorBase):
    name = "local_search"

    def __init__(self, root_dir: Path):
        self.root_dir = Path(root_dir)

    def execute(self, operation: str, payload: dict[str, Any]) -> dict[str, Any]:
        from clawflow.tools.file_tools import LocalDocumentSearchTool
        from clawflow.tools.base import ToolContext
        from clawflow.config.settings import load_settings
        from clawflow.memory.memory_store import MemoryStore

        if operation != "search":
            raise ValueError(f"unsupported local_search operation: {operation}")
        settings = load_settings()
        memory = MemoryStore(settings.database_path)
        return LocalDocumentSearchTool().run(payload, ToolContext(settings=settings, memory=memory)).data

