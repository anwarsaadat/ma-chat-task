from __future__ import annotations
from typing import Dict, Any, List
import os, json
from ..core.message_bus import Message, MessageBus
from ..core.planner import Planner
from ..core.utils import now_ts, gen_id, to_json, confidence_from_counts
from ..memory.stores import ConversationMemory, KnowledgeBase, AgentStateMemory
from .research import ResearchAgent
from .analysis import AnalysisAgent
from .memory import MemoryAgent
from src.core.llm import LLMClient
from dotenv import load_dotenv

load_dotenv()


class Coordinator:
    def __init__(self, cfg: Dict[str,Any] | None = None, kb_path: str | None = None, log_dir: str | None = None):
        self.cfg = cfg or {}
        self.bus = MessageBus()
        self.planner = Planner()

        self.convo = ConversationMemory()
        self.kb = KnowledgeBase(vector_dim=256)
        self.agent_state = AgentStateMemory()
        self.memory = MemoryAgent(self.convo, self.kb, self.agent_state)

        self.research = ResearchAgent(kb_path=kb_path)
        self.analysis = AnalysisAgent()

        self.log_dir = log_dir or os.path.abspath(os.path.join(os.getcwd(), "outputs"))
        os.makedirs(self.log_dir, exist_ok=True)
        self.trace_path = os.path.join(self.log_dir, "trace.jsonl")

        self.llm = LLMClient() if os.getenv("GROQ_API_KEY") else None

    def _trace(self, event: str, payload: Dict[str,Any]):
        record = {"timestamp": now_ts(), "event": event, "payload": payload}
        with open(self.trace_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def classify_intent(self, text: str) -> str:
        if self.llm:
            plan = self.llm.classify_or_plan(text)
            if plan:
                self._trace("llm.intent", {"text": text, "llm_plan": plan})

        t = text.lower()
        if "what did we" in t or "earlier" in t or "remember" in t or "discuss" in t:
            return "memory_query"
        if "compare" in t and "recommend" in t:
            return "compare_recommend"
        if any(k in t for k in ["research", "analyze", "analyze their", "trade-offs", "tradeoffs", "papers", "architectures", "efficiency", "methodologies", "challenges"]):
            if "paper" in t or "papers" in t or "recent" in t:
                return "multi_step"
            return "complex_research"
        if any(k in t for k in ["neural network", "neural networks", "transformer", "optimizer", "reinforcement learning", "rl"]):
            return "simple_query"
        return "simple_query"

    def _infer_topics(self, text: str) -> List[str]:
        words = [w for w in __import__("re").findall(r"[A-Za-z0-9_-]+", text) if len(w) > 3]
        return list(dict.fromkeys(words))[:6]

    def handle_user_query(self, text: str) -> str:
        return self.handle(text)

    def handle(self, text: str) -> str:
        self.memory.record_turn(role="user", content=text)
        intent = self.classify_intent(text)
        self._trace("intent", {"text": text, "intent": intent})

        prior_hits = self.kb.search_vector(text, top_k=1)
        overlap = prior_hits[0][1] if prior_hits else 0.0
        plan = self.planner.make_plan(intent, text)
        self._trace("plan", {"intent": intent, "steps":[{"agent":s.agent,"action":s.action,"payload":s.payload} for s in plan]})
        research_payload = None
        analysis_payload = None

        try:
            for step in plan:
                self.bus.send(Message(sender="manager", recipient=step.agent, type=step.action, payload=step.payload))

                if step.agent == "memory" and step.action == "recall":
                    recall = self.memory.recall(step.payload["query"])
                    self._trace("memory.recall", recall)
                    if recall["matches"]:
                        lines = []
                        for m in recall["matches"][:3]:
                            lines.append(f"- {', '.join(m['topic'])}: {m['content'][:140]}... (conf={m['confidence']})")
                        answer = "Here's what I found in memory:\n" + "\n".join(lines)
                    else:
                        answer = "I couldn't find relevant memory for that query."
                    self.memory.record_turn(role="manager", content=answer)
                    return answer

                if step.agent == "research" and step.action == "search":
                    research_payload = self.research.search(step.payload.get("query",""))
                    self._trace("research.result", {"query": step.payload.get("query",""), "num_results": len(research_payload.get("results",[])), "confidence": research_payload.get("confidence",0.0)})
                    if intent == "simple_query":
                        bullets = [f"- {r.get('title')}: {r.get('summary')}" for r in research_payload["results"][:6]]
                        answer = "Main findings:\n" + "\n".join(bullets)
                        topics = self._infer_topics(text)
                        conf = confidence_from_counts(len(research_payload.get("results",[])), overlap)
                        self.memory.store_knowledge(topic=topics, content=answer, source="research_agent", agent="research", confidence=conf, provenance={"query": text})
                        self.memory.store_agent_state(agent="research", task=text, result_summary=answer[:300], metrics={"confidence": conf})
                        self.memory.record_turn(role="manager", content=answer)
                        return answer

                if step.agent == "analysis" and step.action == "analyze":
                    if not research_payload:
                        research_payload = self.research.search(text)
                        self._trace("research.fallback_for_analysis", {"query": text, "num_results": len(research_payload.get("results",[]))})
                    analysis_payload = self.analysis.analyze(research_payload, step.payload.get("instructions",""))
                    self._trace("analysis.result", analysis_payload)

            if self.llm:
                llm_summary = self.llm.classify_or_plan(f"Synthesize answer for: {text}")
                if llm_summary:
                    self._trace("llm.synthesis", {"summary": llm_summary})
                    self.memory.record_turn(role="manager", content=llm_summary)
                    return llm_summary

            answer = self._synthesize(intent, text, research_payload, analysis_payload, overlap)
            topics = self._infer_topics(text)
            conf = confidence_from_counts(len(research_payload["results"]) if research_payload else 0, float(overlap))
            self.memory.store_knowledge(topic=topics, content=answer, source="manager_synthesis", agent="manager", confidence=conf, provenance={"intent": intent})
            self.memory.store_agent_state(agent="manager", task=intent, result_summary=answer[:300], metrics={"confidence": conf})
            self.memory.record_turn(role="manager", content=answer)
            return answer

        except Exception as e:
            err_msg = f"Error: {e}"
            self._trace("error", {"error": str(e)})
            fallback = "Something went wrong. Try rephrasing the question or ask a simpler query."
            self.memory.record_turn(role="manager", content=fallback)
            return fallback

    def _synthesize(self, intent: str, query: str, research_payload: Dict[str,Any] | None, analysis_payload: Dict[str,Any] | None, overlap: float) -> str:
        if intent == "complex_research" and research_payload and analysis_payload:
            if analysis_payload.get("type") == "transformer_efficiency":
                lines = ["Transformer Efficiency (heuristic):"]
                for row in analysis_payload["table"]:
                    lines.append(f"- {row['architecture']}: {row['attention']} | efficiency≈{row['efficiency_score']}")
                return "\n".join(lines) + f"\nSummary: {analysis_payload.get('summary','')}"
            if analysis_payload.get("type") == "optimizer_comparison":
                lines = ["Optimizer ranking (heuristic):"]
                for r in analysis_payload["ranking"]:
                    lines.append(f"- {r['name']}: score={r['score']} ({r['reason']})")
                lines.append(analysis_payload.get("notes",""))
                return "\n".join(lines)
            return "Analysis summary:\n" + analysis_payload.get("summary","No details available.")

        if intent == "multi_step" and research_payload and analysis_payload:
            lines = [f"Research: {[r.get('title') for r in research_payload.get('results',[])]}"]
            lines.append("Analysis: " + analysis_payload.get("summary",""))
            lines.append("Common challenges: " + ", ".join(analysis_payload.get("challenges",[])))
            return "\n".join(lines)

        if intent == "compare_recommend" and analysis_payload:
            if analysis_payload.get("type") == "generic_summary" and "summary" in analysis_payload:
                return "Comparison:\n" + analysis_payload["summary"]
            return "Comparison result:\n" + to_json(analysis_payload)

        if research_payload:
            bullets = [f"- {r.get('title')}: {r.get('summary')}" for r in research_payload.get("results",[])]
            return "Findings:\n" + "\n".join(bullets)
        return "No findings."