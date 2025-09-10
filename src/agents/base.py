class BaseAgent:
    def __init__(self, name: str):
        self.name = name

    def respond(self, query: str) -> str:
        return f"TODO: implement response in {self.name}"