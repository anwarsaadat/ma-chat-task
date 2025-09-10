# src/memory/vector_store.py
from __future__ import annotations
import math, re
from typing import Dict, List, Tuple

class SimpleVectorStore:
    """
    Deterministic hashed bag-of-words embedder with cosine similarity.
    No external deps.
    """
    def __init__(self, dim: int = 256) -> None:
        self.dim = dim
        self.store: Dict[str, List[float]] = {}
        self.texts: Dict[str, str] = {}

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"[a-zA-Z0-9_]+", text.lower())

    def embed(self, text: str) -> List[float]:
        vec = [0.0] * self.dim
        tokens = self._tokenize(text)
        if not tokens:
            return vec
        for tok in tokens:
            h = (hash(tok) % self.dim + self.dim) % self.dim
            vec[h] += 1.0
        norm = math.sqrt(sum(v*v for v in vec)) or 1.0
        return [v / norm for v in vec]

    def add(self, key: str, text: str) -> None:
        self.texts[key] = text
        self.store[key] = self.embed(text)

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        qv = self.embed(query)
        results: List[Tuple[str, float]] = []
        for k, v in self.store.items():
            score = sum(a*b for a,b in zip(qv, v))
            results.append((k, float(score)))
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
