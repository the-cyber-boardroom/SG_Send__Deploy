# ═══════════════════════════════════════════════════════════════════════════════
# Model Info Schema — single model from Ollama /api/tags
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                  import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Str                   import Safe_Str
from osbot_utils.type_safe.primitives.core.Safe_UInt                  import Safe_UInt
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__List import Type_Safe__List

class Schema__Model__Info(Type_Safe):                                  # Single model from Ollama
    name        : Safe_Str                                             # e.g. "gemma3:4b"
    size        : Safe_UInt                                            # size in bytes
    modified_at : Safe_Str                                             # ISO timestamp from Ollama

class List__Model__Infos(Type_Safe__List):                             # Typed list of model infos
    expected_type = Schema__Model__Info
