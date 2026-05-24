from __future__ import annotations

import argparse
import re
from pathlib import Path


def class_name(name: str) -> str:
    return "".join(part.capitalize() for part in re.findall(r"[a-zA-Z0-9]+", name)) + "Tool"


def create_tool(name: str, risk: str = "low", base_dir: str | Path = "clawflow/tools") -> Path:
    slug = re.sub(r"[^a-zA-Z0-9_]+", "_", name.strip().lower()).strip("_")
    path = Path(base_dir) / f"{slug}_tool.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    cls = class_name(slug)
    path.write_text(
        f'''from clawflow.core.schema import ToolResult
from clawflow.tools.base import BaseTool, ToolContext


class {cls}(BaseTool):
    name = "{slug}"
    description = "Generated ClawFlow tool template. Replace implementation with a real data flow."
    risk_level = "{risk}"
    input_schema = {{}}
    output_schema = {{"message": "string"}}

    def run(self, args: dict, context: ToolContext) -> ToolResult:
        return ToolResult(ok=True, data={{"message": "tool template executed", "args": args}})
''',
        encoding="utf-8",
    )
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a BaseTool template.")
    parser.add_argument("name")
    parser.add_argument("--risk", choices=["low", "medium", "high"], default="low")
    args = parser.parse_args()
    print(create_tool(args.name, args.risk))


if __name__ == "__main__":
    main()
