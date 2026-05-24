from __future__ import annotations

import re
from collections import Counter


def _tokens(text: str) -> list[str]:
    return [token.lower() for token in re.findall(r"[\w\u4e00-\u9fff]+", text)]


class KeywordRetriever:
    def retrieve(self, query: str, chunks: list[dict], limit: int = 6) -> list[dict]:
        q = Counter(_tokens(query))
        scored = []
        for chunk in chunks:
            c = Counter(_tokens(chunk["text"]))
            score = sum(min(q[token], c.get(token, 0)) for token in q)
            if score:
                scored.append((score, chunk))
        scored.sort(key=lambda item: -item[0])
        return [{**chunk, "score": score} for score, chunk in scored[:limit]]

