from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from clawflow.core.schema import ToolResult
from clawflow.tools.base import BaseTool, ToolContext


class DynamicPluginTool(BaseTool):
    def __init__(self, meta: dict[str, Any]):
        self.name = meta["name"]
        self.description = meta.get("description", "Dynamic ClawFlow plugin tool")
        self.risk_level = meta.get("risk_level", "low")
        self.input_schema = meta.get("input_schema", {})
        self.output_schema = meta.get("output_schema", {})
        self.enabled = bool(meta.get("enabled", True))
        self.operation = meta.get("operation", "workspace_stats")
        self.meta = meta

    def run(self, args: dict, context: ToolContext) -> ToolResult:
        if self.operation == "workspace_stats":
            files = [p for p in context.settings.root_dir.rglob("*") if p.is_file() and ".git" not in p.parts]
            data = {
                "file_count": len(files),
                "python_files": len([p for p in files if p.suffix == ".py"]),
                "markdown_files": len([p for p in files if p.suffix == ".md"]),
                "generated_at": time.time(),
            }
            path = context.settings.root_dir / "outputs" / "plugin_workspace_stats.json"
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            return ToolResult(ok=True, data=data, artifacts=[str(path)])
        if self.operation == "echo":
            text = str(args.get("text", context.user_input))
            return ToolResult(ok=True, data={"text": text, "plugin": self.name})
        return ToolResult(ok=False, error=f"unsupported plugin operation: {self.operation}")


class PluginLoader:
    def __init__(self, manifest_path: Path):
        self.manifest_path = manifest_path

    def load_manifest(self) -> dict[str, Any]:
        if not self.manifest_path.exists():
            return {"plugins": []}
        return json.loads(self.manifest_path.read_text(encoding="utf-8"))

    def load_into(self, registry) -> list[str]:
        manifest = self.load_manifest()
        loaded: list[str] = []
        for plugin in manifest.get("plugins", []):
            for tool_meta in plugin.get("tools", []):
                tool = DynamicPluginTool(tool_meta | {"plugin": plugin.get("name")})
                registry.register(tool)
                loaded.append(tool.name)
        return loaded

