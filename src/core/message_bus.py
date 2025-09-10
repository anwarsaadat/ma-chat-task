# src/core/message_bus.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class Message:
    sender: str
    recipient: str
    type: str
    payload: Dict[str, Any] = field(default_factory=dict)

class MessageBus:
    def __init__(self) -> None:
        self.trace: List[Message] = []

    def send(self, msg: Message) -> None:
        # capture the message; for this prototype agents are called synchronously
        self.trace.append(msg)

    def dump(self) -> List[Message]:
        return list(self.trace)
