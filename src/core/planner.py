# src/core/planner.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List

@dataclass
class PlanStep:
    agent: str
    action: str
    payload: Dict[str, Any]

class Planner:
    """
    Very small rule-based planner mapping intents to agent steps.
    Intent labels: simple_query, complex_research, memory_query, multi_step, compare_recommend
    """
    def make_plan(self, intent: str, query: str) -> List[PlanStep]:
        steps: List[PlanStep] = []
        if intent == "memory_query":
            steps.append(PlanStep(agent="memory", action="recall", payload={"query": query}))
            return steps

        if intent == "simple_query":
            steps.append(PlanStep(agent="research", action="search", payload={"query": query}))
            return steps

        if intent == "complex_research":
            steps.append(PlanStep(agent="research", action="search", payload={"query": query}))
            steps.append(PlanStep(agent="analysis", action="analyze", payload={"instructions": "efficiency_and_tradeoffs"}))
            return steps

        if intent == "multi_step":
            steps.append(PlanStep(agent="research", action="search", payload={"query": query}))
            steps.append(PlanStep(agent="analysis", action="analyze", payload={"instructions": "methodologies_and_challenges"}))
            return steps

        if intent == "compare_recommend":
            steps.append(PlanStep(agent="research", action="search", payload={"query": query}))
            steps.append(PlanStep(agent="analysis", action="analyze", payload={"instructions": "compare_and_recommend"}))
            return steps

        # default fallback
        steps.append(PlanStep(agent="research", action="search", payload={"query": query}))
        return steps
