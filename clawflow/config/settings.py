from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def _parse_value(value: str) -> Any:
    value = value.strip().strip("'\"")
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value


def _simple_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, data)]
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if ":" not in raw:
            continue
        key, value = raw.strip().split(":", 1)
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if value.strip() == "":
            child: dict[str, Any] = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = _parse_value(value)
    return data


@dataclass(slots=True)
class Settings:
    root_dir: Path = ROOT
    storage_dir: Path = ROOT / "outputs"
    database_path: Path = ROOT / "outputs" / "clawflow.sqlite3"
    trace_path: Path = ROOT / "outputs" / "trace.jsonl"
    checkpoint_dir: Path = ROOT / "outputs" / "checkpoints"
    screenshot_dir: Path = ROOT / "docs" / "assets" / "screenshots"
    llm_mode: str = "local"
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    logging_level: str = "INFO"
    web_host: str = "127.0.0.1"
    web_port: int = 8000
    policy: dict[str, str] = field(
        default_factory=lambda: {"low": "allow", "medium": "ask", "high": "ask"}
    )
    shell_allowlist: list[str] = field(
        default_factory=lambda: ["ls", "dir", "pwd", "echo", "python --version", "pytest", "tree"]
    )
    benchmark_tasks: list[str] = field(default_factory=list)

    def ensure_dirs(self) -> None:
        for path in [
            self.storage_dir,
            self.checkpoint_dir,
            self.screenshot_dir,
            self.root_dir / "outputs" / "outbox",
            self.root_dir / "outputs" / "calendar",
            self.root_dir / "docs" / "assets" / "diagrams",
            self.root_dir / "docs" / "assets" / "figures",
            self.root_dir / "slides",
        ]:
            path.mkdir(parents=True, exist_ok=True)


def load_settings(config_path: str | Path | None = None) -> Settings:
    path = Path(config_path) if config_path else ROOT / "config.yaml"
    raw = _simple_yaml(path)
    storage_dir = Path(raw.get("storage", {}).get("dir", ROOT / "outputs"))
    settings = Settings(
        storage_dir=storage_dir,
        database_path=Path(raw.get("storage", {}).get("database", storage_dir / "clawflow.sqlite3")),
        trace_path=Path(raw.get("storage", {}).get("trace_jsonl", storage_dir / "trace.jsonl")),
        checkpoint_dir=Path(raw.get("storage", {}).get("checkpoint_dir", storage_dir / "checkpoints")),
        screenshot_dir=Path(raw.get("screenshots", {}).get("dir", ROOT / "docs" / "assets" / "screenshots")),
        llm_mode=os.getenv("CLAWFLOW_LLM_MODE", str(raw.get("llm", {}).get("mode", "local"))),
        openai_api_key=os.getenv("OPENAI_API_KEY", str(raw.get("llm", {}).get("api_key", ""))),
        openai_base_url=os.getenv("OPENAI_BASE_URL", str(raw.get("llm", {}).get("base_url", "https://api.openai.com/v1"))),
        openai_model=os.getenv("OPENAI_MODEL", str(raw.get("llm", {}).get("model", "gpt-4o-mini"))),
        logging_level=str(raw.get("logging", {}).get("level", "INFO")),
        web_host=str(raw.get("web", {}).get("host", "127.0.0.1")),
        web_port=int(raw.get("web", {}).get("port", 8000)),
        policy=dict(raw.get("policy", {"low": "allow", "medium": "ask", "high": "ask"})),
    )
    shell_allowlist = raw.get("shell", {}).get("allowlist", None)
    if isinstance(shell_allowlist, list):
        settings.shell_allowlist = shell_allowlist
    benchmark_tasks = raw.get("benchmark", {}).get("tasks", None)
    if isinstance(benchmark_tasks, list):
        settings.benchmark_tasks = benchmark_tasks
    settings.ensure_dirs()
    return settings
