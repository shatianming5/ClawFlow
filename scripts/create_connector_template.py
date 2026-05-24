from __future__ import annotations

import argparse
import re
from pathlib import Path


def slugify(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]+", "_", name.strip().lower()).strip("_") or "generated_connector"


def class_name(name: str) -> str:
    return "".join(part.capitalize() for part in re.findall(r"[a-zA-Z0-9]+", name)) + "Connector"


def create_connector(
    name: str,
    operation: str = "sync",
    base_dir: str | Path = "clawflow/connectors/generated",
) -> Path:
    slug = slugify(name)
    op = slugify(operation)
    root = Path(base_dir)
    root.mkdir(parents=True, exist_ok=True)
    (root / "__init__.py").touch()
    path = root / f"{slug}.py"
    cls = class_name(slug)
    path.write_text(
        f'''from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from clawflow.connectors.base import ConnectorBase


class {cls}(ConnectorBase):
    """Generated MCP-like connector with a local durable adapter.

    Replace `_call_remote_service` when wiring a production API. The local
    implementation records real operation payloads to JSONL so tests, traces
    and demos observe an actual data flow instead of a fixed response.
    """

    name = "{slug}"
    default_operation = "{op}"

    def __init__(self, output_dir: str | Path = "outputs/connectors/{slug}"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.events_path = self.output_dir / "events.jsonl"

    def execute(self, operation: str, payload: dict[str, Any]) -> dict[str, Any]:
        operation = operation or self.default_operation
        record = {{
            "created_at": time.time(),
            "connector": self.name,
            "operation": operation,
            "payload": payload,
            "adapter": "local_jsonl",
        }}
        with self.events_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\\n")
        return {{
            "ok": True,
            "connector": self.name,
            "operation": operation,
            "events_path": str(self.events_path),
            "record": record,
        }}

    def _call_remote_service(self, operation: str, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("Replace local JSONL adapter with a production connector backend.")
''',
        encoding="utf-8",
    )
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a MCP-like Connector template with local JSONL persistence.")
    parser.add_argument("name")
    parser.add_argument("--operation", default="sync")
    args = parser.parse_args()
    print(create_connector(args.name, args.operation))


if __name__ == "__main__":
    main()
