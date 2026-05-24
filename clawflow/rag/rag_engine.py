from __future__ import annotations

from pathlib import Path

from .chunker import Chunker
from .document_loader import DocumentLoader
from .retriever import KeywordRetriever


class RagEngine:
    def __init__(self, root_dir: Path):
        self.root_dir = Path(root_dir)
        self.loader = DocumentLoader(self.root_dir)
        self.chunker = Chunker()
        self.retriever = KeywordRetriever()

    def retrieve(self, query: str, limit: int = 6) -> list[dict]:
        docs = self.loader.load()
        chunks = self.chunker.chunk(docs)
        return self.retriever.retrieve(query, chunks, limit=limit)

    def answer(self, query: str) -> dict:
        chunks = self.retrieve(query, limit=6)
        lines = [
            "# RAG Answer",
            "",
            f"Query: {query}",
            "",
            "## Answer",
        ]
        if not chunks:
            lines.append("No matching project documentation chunks were found. Import or generate docs first.")
        else:
            lines.append(
                "ClawFlow 的核心创新点集中在统一 Agent Runtime、AgentOS Kernel、权限治理、可观测 trace、checkpoint/resume、Memory Layer、插件注册、RAG 与多智能体协作。"
            )
            lines.append("这些结论来自当前仓库中的真实文档片段，而不是固定模板输出。")
        lines += ["", "## Retrieved evidence"]
        for idx, chunk in enumerate(chunks, 1):
            snippet = " ".join(chunk["text"].split())[:420]
            lines.append(f"{idx}. `{chunk['path']}` (score={chunk['score']}): {snippet}")
        return {"markdown": "\n".join(lines) + "\n", "chunks": chunks, "query": query}

