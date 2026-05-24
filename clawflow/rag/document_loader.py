from __future__ import annotations

from pathlib import Path


class DocumentLoader:
    def __init__(self, root_dir: Path):
        self.root_dir = Path(root_dir)

    def load(self, search_paths: list[str] | None = None) -> list[dict]:
        paths = search_paths or ["docs", "README.md", "outputs"]
        docs: list[dict] = []
        for item in paths:
            path = self.root_dir / item
            candidates = path.rglob("*") if path.is_dir() else [path]
            for candidate in candidates:
                if not candidate.exists() or not candidate.is_file():
                    continue
                if candidate.suffix.lower() not in {".md", ".txt", ".py", ".json", ".yaml", ".yml"}:
                    continue
                try:
                    text = candidate.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue
                docs.append({"path": str(candidate.relative_to(self.root_dir)), "text": text})
        return docs

