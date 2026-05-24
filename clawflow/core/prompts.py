from __future__ import annotations

import sqlite3
import time
from pathlib import Path
from typing import Any


DEFAULT_PROMPTS = [
    {
        "name": "research_summary",
        "description": "Project analysis prompt for Runtime-backed research applications.",
        "template": "请分析 {project} 的结构，生成摘要、报告大纲和 TODO 列表。",
        "tags": "research,report,agent-runtime",
    },
    {
        "name": "governance_review",
        "description": "Review tool risk, audit log, and approval boundaries.",
        "template": "请审查 {run_id} 的工具调用风险、权限决策和审计记录。",
        "tags": "governance,audit,safety",
    },
    {
        "name": "rag_answer",
        "description": "Answer questions using retrieved ClawFlow project documentation.",
        "template": "请根据检索到的文档片段回答：{question}",
        "tags": "rag,knowledge-base,retrieval",
    },
]


class PromptTemplateRegistry:
    """SQLite-backed prompt template registry for repeatable Agent Runtime applications."""

    def __init__(self, database_path: Path):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self.seed_defaults()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS prompt_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT NOT NULL,
                    template TEXT NOT NULL,
                    tags TEXT,
                    usage_count INTEGER NOT NULL DEFAULT 0,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
                """
            )

    def seed_defaults(self) -> None:
        for item in DEFAULT_PROMPTS:
            self.upsert(item["name"], item["template"], item["description"], item["tags"], increment=False)

    def upsert(self, name: str, template: str, description: str = "", tags: str = "", increment: bool = False) -> int:
        now = time.time()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO prompt_templates(name, description, template, tags, created_at, updated_at)
                VALUES(?, ?, ?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    description=excluded.description,
                    template=excluded.template,
                    tags=excluded.tags,
                    updated_at=excluded.updated_at
                """,
                (name, description, template, tags, now, now),
            )
            row = conn.execute("SELECT id FROM prompt_templates WHERE name=?", (name,)).fetchone()
        if increment:
            self.increment_usage(name)
        return int(row["id"])

    def list(self, limit: int = 100) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM prompt_templates ORDER BY name ASC LIMIT ?", (limit,)).fetchall()
        return [dict(row) for row in rows]

    def get(self, name: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM prompt_templates WHERE name=?", (name,)).fetchone()
        return dict(row) if row else None

    def render(self, name: str, variables: dict[str, Any]) -> str:
        row = self.get(name)
        if not row:
            raise KeyError(f"Prompt template not found: {name}")
        self.increment_usage(name)
        return row["template"].format(**variables)

    def increment_usage(self, name: str) -> None:
        with self._connect() as conn:
            conn.execute("UPDATE prompt_templates SET usage_count=usage_count+1, updated_at=? WHERE name=?", (time.time(), name))

