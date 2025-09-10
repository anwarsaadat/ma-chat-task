# src/memory/stores.py
from __future__ import annotations
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from .vector_store import SimpleVectorStore
import time

@dataclass
class ConversationTurn:
    id: str
    timestamp: str
    role: str  # user | manager | agent
    content: str
    metadata: Dict = field(default_factory=dict)

@dataclass
class KnowledgeRecord:
    id: str
    timestamp: str
    topic: List[str]
    content: str
    source: str
    agent: str
    confidence: float
    provenance: Dict = field(default_factory=dict)

@dataclass
class AgentStateRecord:
    id: str
    timestamp: str
    agent: str
    task: str
    result_summary: str
    metrics: Dict = field(default_factory=dict)

class ConversationMemory:
    def __init__(self) -> None:
        self.turns: List[ConversationTurn] = []

    def add(self, turn: ConversationTurn) -> None:
        self.turns.append(turn)

    def history(self) -> List[ConversationTurn]:
        return list(self.turns)

    def search(self, keyword: str) -> List[ConversationTurn]:
        key = keyword.lower()
        return [t for t in self.turns if key in t.content.lower()]

class KnowledgeBase:
    def __init__(self, vector_dim: int = 256) -> None:
        self.records: Dict[str, KnowledgeRecord] = {}
        self.vs = SimpleVectorStore(dim=vector_dim)

    def add(self, rec: KnowledgeRecord) -> None:
        self.records[rec.id] = rec
        self.vs.add(rec.id, rec.content + " " + " ".join(rec.topic))

    def get(self, rec_id: str) -> Optional[KnowledgeRecord]:
        return self.records.get(rec_id)

    def search_keyword(self, query: str, top_k: int = 5) -> List[KnowledgeRecord]:
        q = query.lower()
        out = []
        for rec in self.records.values():
            if q in rec.content.lower() or any(q in t.lower() for t in rec.topic):
                out.append(rec)
        return out[:top_k]

    def search_vector(self, query: str, top_k: int = 5) -> List[Tuple[KnowledgeRecord, float]]:
        hits = self.vs.search(query, top_k=top_k)
        out = []
        for rec_id, score in hits:
            rec = self.records.get(rec_id)
            if rec:
                out.append((rec, score))
        return out

class AgentStateMemory:
    def __init__(self) -> None:
        self.records: Dict[str, AgentStateRecord] = {}

    def add(self, rec: AgentStateRecord) -> None:
        self.records[rec.id] = rec

    def list(self) -> List[AgentStateRecord]:
        return list(self.records.values())
