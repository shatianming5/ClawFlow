from __future__ import annotations

import json
import os
import re
from pathlib import Path

from clawflow.core.schema import ToolResult
from clawflow.tools.base import BaseTool, ToolContext


TEXT_EXTENSIONS = {".md", ".txt", ".py", ".json", ".yaml", ".yml", ".toml", ".html", ".css", ".js", ".csv"}


def safe_path(root: Path, path: str | Path) -> Path:
    root = root.resolve()
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved = candidate.resolve()
    if root != resolved and root not in resolved.parents:
        raise ValueError(f"path escapes workspace: {path}")
    return resolved


def _read_text(path: Path, limit: int = 120_000) -> str:
    data = path.read_text(encoding="utf-8", errors="ignore")
    if len(data) > limit:
        return data[:limit] + "\n\n[truncated]\n"
    return data


class ReadFileTool(BaseTool):
    name = "read_file"
    description = "Read a UTF-8 text file from the workspace."
    risk_level = "low"
    input_schema = {"path": "relative workspace path"}

    def run(self, args: dict, context: ToolContext) -> ToolResult:
        path = safe_path(context.settings.root_dir, args["path"])
        if not path.exists() or not path.is_file():
            return ToolResult(ok=False, error=f"file not found: {args['path']}")
        return ToolResult(ok=True, data={"path": str(path), "content": _read_text(path)})


class WriteFileTool(BaseTool):
    name = "write_file"
    description = "Write a UTF-8 text file inside the workspace."
    risk_level = "low"
    input_schema = {"path": "relative workspace path", "content": "text content"}

    def run(self, args: dict, context: ToolContext) -> ToolResult:
        path = safe_path(context.settings.root_dir, args["path"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(str(args.get("content", "")), encoding="utf-8")
        return ToolResult(ok=True, data={"path": str(path), "bytes": path.stat().st_size}, artifacts=[str(path)])


class ListFilesTool(BaseTool):
    name = "list_files"
    description = "List workspace files with safe ignore defaults."
    risk_level = "low"
    input_schema = {"path": "relative path", "max_files": "integer"}

    def run(self, args: dict, context: ToolContext) -> ToolResult:
        base = safe_path(context.settings.root_dir, args.get("path", "."))
        max_files = int(args.get("max_files", 200))
        ignore = {".git", ".venv", "__pycache__", ".pytest_cache", "node_modules"}
        files: list[str] = []
        if base.is_file():
            files.append(str(base.relative_to(context.settings.root_dir)))
        else:
            for dirpath, dirnames, filenames in os.walk(base):
                dirnames[:] = [d for d in dirnames if d not in ignore]
                for filename in sorted(filenames):
                    path = Path(dirpath) / filename
                    files.append(str(path.relative_to(context.settings.root_dir)))
                    if len(files) >= max_files:
                        break
                if len(files) >= max_files:
                    break
        return ToolResult(ok=True, data={"root": str(base), "files": files, "count": len(files)})


class SummarizeFileTool(BaseTool):
    name = "summarize_file"
    description = "Summarize a text file by extracting headings, first paragraphs, and rough metrics."
    risk_level = "low"
    input_schema = {"path": "relative workspace path"}

    def run(self, args: dict, context: ToolContext) -> ToolResult:
        path = safe_path(context.settings.root_dir, args["path"])
        if not path.exists():
            return ToolResult(ok=False, error=f"file not found: {args['path']}")
        text = _read_text(path, 80_000)
        headings = [line.strip("# ").strip() for line in text.splitlines() if line.startswith("#")][:10]
        words = re.findall(r"[\w\u4e00-\u9fff]+", text)
        preview = "\n".join([line for line in text.splitlines() if line.strip()][:12])
        summary = {
            "path": str(path.relative_to(context.settings.root_dir)),
            "line_count": text.count("\n") + 1,
            "word_count": len(words),
            "headings": headings,
            "preview": preview[:1200],
        }
        return ToolResult(ok=True, data=summary)


class LocalDocumentSearchTool(BaseTool):
    name = "local_document_search"
    description = "Search local project documents and source files with keyword scoring."
    risk_level = "low"
    input_schema = {"query": "search query", "path": "search root", "limit": "max hits"}

    def run(self, args: dict, context: ToolContext) -> ToolResult:
        query = str(args.get("query", ""))
        terms = [term.lower() for term in re.findall(r"[\w\u4e00-\u9fff]+", query)]
        root = safe_path(context.settings.root_dir, args.get("path", "."))
        limit = int(args.get("limit", 8))
        hits = []
        for path in root.rglob("*") if root.is_dir() else [root]:
            if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            if any(part in {".git", ".venv", "__pycache__", "node_modules"} for part in path.parts):
                continue
            try:
                text = _read_text(path, 50_000)
            except Exception:
                continue
            lower = text.lower()
            score = sum(lower.count(term) for term in terms) if terms else 0
            if score:
                snippet_start = min([lower.find(term) for term in terms if term in lower] or [0])
                snippet = text[max(0, snippet_start - 120): snippet_start + 420]
                hits.append(
                    {
                        "path": str(path.relative_to(context.settings.root_dir)),
                        "score": score,
                        "snippet": snippet.replace("\n", " ")[:500],
                    }
                )
        hits.sort(key=lambda item: -item["score"])
        return ToolResult(ok=True, data={"query": query, "hits": hits[:limit], "count": len(hits[:limit])})


def default_file_tools() -> list[BaseTool]:
    return [ReadFileTool(), WriteFileTool(), ListFilesTool(), SummarizeFileTool(), LocalDocumentSearchTool()]

