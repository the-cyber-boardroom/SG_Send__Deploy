# ═══════════════════════════════════════════════════════════════════════════════
# Chat Session Status — active or archived
# ═══════════════════════════════════════════════════════════════════════════════

from enum import Enum

class Enum__Chat__Session_Status(str, Enum):
    ACTIVE   = "active"
    ARCHIVED = "archived"

    def __str__(self): return self.value
