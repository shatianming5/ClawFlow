from pathlib import Path

from clawflow.config.settings import load_settings
from clawflow.memory.memory_store import MemoryStore
from clawflow.tools.base import ToolContext
from clawflow.tools.registry import create_default_registry


def test_plugin_loader_registers_and_executes_plugin_tool():
    registry = create_default_registry(Path(".").resolve())
    assert registry.has("plugin_workspace_stats")
    settings = load_settings()
    result = registry.execute("plugin_workspace_stats", {}, ToolContext(settings=settings, memory=MemoryStore(settings.database_path)))
    assert result.ok
    assert result.data["file_count"] > 0

