from .config import Config

try:
    from groq import Groq
except ImportError:
    Groq = None

class LLMClient:
    def __init__(self):
        self.enabled = Config.USE_LLM and Groq is not None
        if self.enabled:
            self.client = Groq(api_key=Config.GROQ_API_KEY)

    def classify_or_plan(self, query: str) -> str:
        if not self.enabled:
            return None

        try:
            resp = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",  # Groq free-tier model
                messages=[
                    {"role": "system", "content": "You are a task planner for a multi-agent system."},
                    {"role": "user", "content": query}
                ],
                max_tokens=100,
            )
            return resp.choices[0].message.content
        except Exception:
            return None