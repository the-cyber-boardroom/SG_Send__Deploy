# ═══════════════════════════════════════════════════════════════════════════════
# LLM Message Role — user, assistant, system, tool
# ═══════════════════════════════════════════════════════════════════════════════

from enum import Enum

class Enum__LLM__Role(str, Enum):
    SYSTEM    = "system"
    USER      = "user"
    ASSISTANT = "assistant"
    TOOL      = "tool"

    def __str__(self): return self.value
