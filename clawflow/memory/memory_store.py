from __future__ import annotations

import json
import re
import sqlite3
import time
from pathlib import Path
from typing import Any


class MemoryStore:
    def __init__(self, database_path: Path):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    hit_count INTEGER NOT NULL DEFAULT 0,
                    created_at REAL NOT NULL
                )
                """
            )

    def add_memory(self, text: str, metadata: dict[str, Any] | None = None) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO memories(text, metadata_json, created_at) VALUES(?, ?, ?)",
                (text, json.dumps(metadata or {}, ensure_ascii=False), time.time()),
            )
            return int(cur.lastrowid)

    def list_memory(self, limit: int = 100) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM memories ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [self._row_to_dict(row) for row in rows]

    def search_memory(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        terms = [term.lower() for term in re.findall(r"[\w\u4e00-\u9fff]+", query)]
        rows = self.list_memory(limit=500)
        scored: list[tuple[int, dict[str, Any]]] = []
        for row in rows:
            haystack = (row["text"] + " " + json.dumps(row["metadata"], ensure_ascii=False)).lower()
            score = sum(1 for term in terms if term in haystack)
            if score:
                scored.append((score, row))
        scored.sort(key=lambda item: (-item[0], -item[1]["created_at"]))
        ids = [row["id"] for _, row in scored[:limit]]
        if ids:
            with self._connect() as conn:
                conn.executemany("UPDATE memories SET hit_count=hit_count+1 WHERE id=?", [(mid,) for mid in ids])
        return [row for _, row in scored[:limit]]

    def delete_memory(self, memory_id: int) -> bool:
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM memories WHERE id=?", (memory_id,))
            return cur.rowcount > 0

    def _row_to_dict(self, row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        data["metadata"] = json.loads(data.pop("metadata_json") or "{}")
        return data

