"""Runtime configuration toggles (skeleton)."""
from __future__ import annotations
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    APP_NAME: str = "Simple MultiAgent Chat System"
    LOG_DIR: str = os.getenv("LOG_DIR", "outputs")
    VECTOR_DIM: int = int(os.getenv("VECTOR_DIM", "256"))
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    USE_LLM = bool(GROQ_API_KEY)