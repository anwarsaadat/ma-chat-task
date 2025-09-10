from __future__ import annotations
from typing import Dict, Any, List
from ..memory.stores import ConversationMemory, KnowledgeBase, AgentStateMemory, KnowledgeRecord, ConversationTurn, AgentStateRecord
from ..core.utils import now_ts, gen_id, to_json

class MemoryAgent:
    def __init__(self, conversation: ConversationMemory, kb: KnowledgeBase, agent_state: AgentStateMemory):
        self.name = "memory"
        self.convo = conversation
        self.kb = kb
        self.agent_state = agent_state

    # Conversation
    def record_turn(self, role: str, content: str, metadata: Dict[str,Any] | None = None):
        turn = ConversationTurn(id=gen_id("turn"), timestamp=now_ts(), role=role, content=content, metadata=metadata or {})
        self.convo.add(turn)
        return turn

    # Knowledge
    def store_knowledge(self, topic: List[str], content: str, source: str, agent: str, confidence: float, provenance: Dict[str,Any] | None = None):
        rec = KnowledgeRecord(id=gen_id("kn"), timestamp=now_ts(), topic=topic, content=content, source=source, agent=agent, confidence=confidence, provenance=provenance or {})
        self.kb.add(rec)
        return rec

    # Agent state
    def store_agent_state(self, agent: str, task: str, result_summary: str, metrics: Dict[str,Any] | None = None):
        rec = AgentStateRecord(id=gen_id("st"), timestamp=now_ts(), agent=agent, task=task, result_summary=result_summary, metrics=metrics or {})
        self.agent_state.add(rec)
        return rec

    # Recall: keyword + vector
    def recall(self, query: str) -> Dict[str,Any]:
        vec_hits = self.kb.search_vector(query, top_k=5)
        kw_hits = self.kb.search_keyword(query, top_k=5)
        combined = []
        seen = set()
        for rec, score in vec_hits:
            combined.append({"id": rec.id, "topic": rec.topic, "content": rec.content, "confidence": rec.confidence, "similarity": round(float(score),3), "source": rec.source})
            seen.add(rec.id)
        for rec in kw_hits:
            if rec.id not in seen:
                combined.append({"id": rec.id, "topic": rec.topic, "content": rec.content, "confidence": rec.confidence, "similarity": None, "source": rec.source})
        return {"query": query, "matches": combined}
