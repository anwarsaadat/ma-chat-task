from __future__ import annotations
from typing import Dict, Any, List
import json, os
from ..core.utils import now_ts, gen_id

class ResearchAgent:
    def __init__(self, kb_path: str | None = None) -> None:
        self.name = "research"
        # load local KB (JSON array of items)
        if kb_path and os.path.exists(kb_path):
            with open(kb_path, "r", encoding="utf-8") as f:
                self.kb = json.load(f)
        else:
            self.kb = []
        # ensure fallback items (light)
        if not self.kb:
            self.kb = [
                {"title":"Feedforward Neural Networks (MLP)","summary":"Simple layered perceptrons; good for tabular tasks.","tags":["neural networks","mlp"]},
                {"title":"Convolutional Neural Networks (CNN)","summary":"Weight sharing and local fields; strong for images.","tags":["neural networks","cnn"]},
                {"title":"Recurrent Neural Networks (RNN, LSTM)","summary":"Sequence models; LSTM/GRU mitigate vanishing gradients.","tags":["neural networks","rnn","lstm"]},
                {"title":"Transformers","summary":"Self-attention based; scalable with parallel compute.","tags":["transformer","attention"]},
                {"title":"Adam / AdamW","summary":"Adaptive optimizers; good default for many models.","tags":["optimizer","adam","adamw"]},
                {"title":"Gradient Descent Variants","summary":"SGD, momentum, Nesterov; simple and effective.","tags":["optimizer","sgd","momentum"]},
                {"title":"RL Paper: Model-Based RL (2024)","summary":"Focus on sample efficiency and planning.","tags":["reinforcement learning","model-based","2024"]},
            ]

    def search(self, query: str, top_k: int = 6) -> Dict[str, Any]:
        q = query.lower()
        results: List[Dict[str, Any]] = []
        for item in self.kb:
            text = (item.get("title","") + " " + item.get("summary","") + " " + " ".join(item.get("tags",[]))).lower()
            # match if any meaningful token in query appears in text
            tokens = [t for t in q.split() if len(t) > 3]
            if any(tok in text for tok in tokens):
                results.append(item)
        if not results:
            # fallback: return top items
            results = self.kb[:top_k]
        return {"query": query, "results": results[:top_k], "timestamp": now_ts(), "confidence": round(min(1.0, 0.5 + 0.05*len(results)),3), "agent": self.name}
