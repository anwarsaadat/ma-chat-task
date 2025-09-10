"""Dataclasses for memory records (skeleton)."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class ConversationTurn:
    id: str
    timestamp: str
    role: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class KnowledgeRecord:
    id: str
    timestamp: str
    topic: List[str]
    content: str
    source: str
    agent: str
    confidence: float
    provenance: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentStateRecord:
    id: str
    timestamp: str
    agent: str
    task: str
    result_summary: str
    metrics: Dict[str, Any] = field(default_factory=dict)
