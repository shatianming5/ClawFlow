from __future__ import annotations

import re
from abc import ABC, abstractmethod
from collections import Counter
from dataclasses import dataclass
from typing import Any


class VectorStoreBase(ABC):
    """Production vector stores can replace this interface with Chroma, FAISS, or Milvus."""

    @abstractmethod
    def add(self, doc_id: str, text: str, metadata: dict[str, Any] | None = None) -> None:
        raise NotImplementedError

    @abstractmethod
    def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        raise NotImplementedError


def _tokens(text: str) -> list[str]:
    return [token.lower() for token in re.findall(r"[\w\u4e00-\u9fff]+", text)]


@dataclass
class _Doc:
    doc_id: str
    text: str
    metadata: dict[str, Any]
    counts: Counter[str]


class SimpleKeywordVectorStore(VectorStoreBase):
    def __init__(self) -> None:
        self._docs: dict[str, _Doc] = {}

    def add(self, doc_id: str, text: str, metadata: dict[str, Any] | None = None) -> None:
        self._docs[doc_id] = _Doc(doc_id, text, metadata or {}, Counter(_tokens(text)))

    def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        q = Counter(_tokens(query))
        scored: list[tuple[int, _Doc]] = []
        for doc in self._docs.values():
            score = sum(min(q[token], doc.counts.get(token, 0)) for token in q)
            if score:
                scored.append((score, doc))
        scored.sort(key=lambda item: -item[0])
        return [
            {"id": doc.doc_id, "text": doc.text, "metadata": doc.metadata, "score": score}
            for score, doc in scored[:limit]
        ]

