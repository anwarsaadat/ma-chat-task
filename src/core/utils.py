from __future__ import annotations
import datetime, uuid
import json
from typing import Any, Dict
from datetime import datetime, timezone

def now_ts() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

def gen_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"

def to_json(obj: Any) -> str:
    try:
        return json.dumps(obj, ensure_ascii=False, indent=2, default=str)
    except Exception:
        return str(obj)

def confidence_from_counts(num_sources: int, overlap: float) -> float:
    # simple heuristic: more sources and less overlap => higher confidence
    base = min(1.0, 0.4 + 0.15 * num_sources)
    bonus = 0.6 * (1.0 - overlap)
    return round(min(1.0, base + bonus), 3)