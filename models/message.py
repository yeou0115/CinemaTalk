from dataclasses import dataclass
from typing import Optional, Literal

Role = Literal["user", "assistant", "host"]

@dataclass
class Message:
    role: Role
    content: str
    speaker: Optional[str] = None
