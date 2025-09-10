# src/services/app.py
from __future__ import annotations
import os
from ..agents.coordinator import Coordinator

def build_coordinator() -> Coordinator:
    kb_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "knowledge_base.json"))
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "outputs"))
    return Coordinator(cfg=None, kb_path=kb_path, log_dir=log_dir)
