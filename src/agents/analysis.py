from __future__ import annotations
from typing import Dict, Any, List, Tuple

class AnalysisAgent:
    def __init__(self) -> None:
        self.name = "analysis"

    def summarize(self, texts: List[str], max_chars: int = 400) -> str:
        # naive summarizer: join and truncate
        joined = " ".join(texts)
        if len(joined) <= max_chars:
            return joined
        return joined[:max_chars].rsplit(" ", 1)[0] + "..."

    def score_optimizers(self, names: List[str]) -> List[Dict[str, Any]]:
        base = {"sgd":0.6, "momentum":0.65, "rmsprop":0.68, "adam":0.8, "adamw":0.82}
        out = []
        for n in names:
            key = n.lower().replace("-", "").split()[0]
            score = base.get(key, 0.65)
            reason = "widely used" if score>=0.75 else "effective in many settings"
            out.append({"name": n, "score": round(score,3), "reason": reason})
        out.sort(key=lambda x: x["score"], reverse=True)
        return out

    def estimate_transformer_efficiency(self, items: List[Dict[str,Any]]) -> Dict[str,Any]:
        table = []
        for it in items:
            name = it.get("title","unknown")
            tags = [t.lower() for t in it.get("tags",[])]
            if any(k in tags for k in ["performer","reformer","linear-attention","linear"]):
                attn = "O(n) or O(n log n)"
                eff = 0.85
            elif any(k in tags for k in ["longformer","sparse","bigbird"]):
                attn = "Sparse (≈O(n log n))"
                eff = 0.8
            else:
                attn = "Full (O(n^2))"
                eff = 0.6
            table.append({"architecture": name, "attention": attn, "efficiency_score": eff})
        table.sort(key=lambda r: r["efficiency_score"], reverse=True)
        return {"summary":"Estimated efficiency from attention pattern heuristics.", "table": table}

    def analyze(self, research_payload: Dict[str,Any], instructions: str) -> Dict[str,Any]:
        results = research_payload.get("results", [])
        # prepare text blocks
        texts = [r.get("summary","") for r in results]
        if "optimizer" in research_payload.get("query","").lower() or "optimization" in research_payload.get("query","").lower():
            names = [r.get("title","") for r in results]
            ranking = self.score_optimizers(names)
            return {"type":"optimizer_comparison","ranking":ranking,"notes":"Heuristic scoring; task specific tuning required."}

        if "transformer" in research_payload.get("query","").lower() and ("efficiency" in instructions or "tradeoffs" in instructions or "trade-offs" in instructions):
            eff = self.estimate_transformer_efficiency(results)
            return {"type":"transformer_efficiency", **eff}

        # generic summarization and methodology extraction
        summary = self.summarize(texts)
        methodology_points = ["Baseline comparison", "Ablation studies", "Evaluation on benchmarks"]
        common_challenges = ["sample efficiency", "distributional shift", "scalability"]
        return {"type":"generic_summary","summary":summary,"methodologies":methodology_points,"challenges":common_challenges}
