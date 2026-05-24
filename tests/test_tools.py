from pathlib import Path

from clawflow.config.settings import load_settings
from clawflow.memory.memory_store import MemoryStore
from clawflow.tools.base import ToolContext
from clawflow.tools.registry import create_default_registry


def _context():
    settings = load_settings()
    return ToolContext(settings=settings, memory=MemoryStore(settings.database_path))


def test_tool_registry_can_list_and_execute_file_tools():
    registry = create_default_registry(Path(".").resolve())
    names = {tool["name"] for tool in registry.list()}
    assert "read_file" in names
    assert "write_file" in names
    ctx = _context()
    out = registry.execute("write_file", {"path": "outputs/test_file_tool.txt", "content": "hello"}, ctx)
    assert out.ok
    read = registry.execute("read_file", {"path": "outputs/test_file_tool.txt"}, ctx)
    assert read.ok
    assert read.data["content"] == "hello"


def test_shell_tool_blocks_dangerous_command():
    registry = create_default_registry(Path(".").resolve())
    result = registry.execute("shell_command", {"command": "rm -rf outputs"}, _context())
    assert not result.ok
    assert result.metadata["blocked"] is True

