from __future__ import annotations

import json
from pathlib import Path

from clawflow.gateway.api import app


def main() -> dict:
    schema = app.openapi()
    output = Path("docs/openapi.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(schema, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# API Reference",
        "",
        "This document is generated from the live FastAPI app schema by `scripts/export_openapi.py`.",
        "",
        "| Method | Path | Summary |",
        "|---|---|---|",
    ]
    for path, methods in sorted(schema.get("paths", {}).items()):
        for method, meta in sorted(methods.items()):
            if method.lower() not in {"get", "post", "put", "patch", "delete"}:
                continue
            summary = meta.get("summary") or meta.get("operationId") or ""
            lines.append(f"| {method.upper()} | `{path}` | {summary} |")
    Path("docs/api_reference.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return schema


if __name__ == "__main__":
    data = main()
    print(f"exported docs/openapi.json with {len(data.get('paths', {}))} paths")

