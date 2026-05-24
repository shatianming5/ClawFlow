from __future__ import annotations


class Chunker:
    def __init__(self, chunk_size: int = 900, overlap: int = 120):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, docs: list[dict]) -> list[dict]:
        chunks: list[dict] = []
        for doc in docs:
            text = doc["text"]
            start = 0
            idx = 0
            while start < len(text):
                end = min(len(text), start + self.chunk_size)
                chunk_text = text[start:end]
                chunks.append({"id": f"{doc['path']}#{idx}", "path": doc["path"], "text": chunk_text})
                if end == len(text):
                    break
                start = max(0, end - self.overlap)
                idx += 1
        return chunks

