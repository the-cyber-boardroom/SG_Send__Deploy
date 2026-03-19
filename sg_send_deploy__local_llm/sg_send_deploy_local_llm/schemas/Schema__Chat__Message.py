# ═══════════════════════════════════════════════════════════════════════════════
# Chat Message Schema — individual message in a chat session
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                  import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Str                   import Safe_Str
from osbot_utils.type_safe.type_safe_core.collections.Type_Safe__List import Type_Safe__List
from sg_send_deploy_local_llm.schemas.types.Enum__LLM__Role          import Enum__LLM__Role

class Schema__Chat__Message(Type_Safe):                                # Individual chat message
    role    : Enum__LLM__Role                                          # user, assistant, system, tool
    content : Safe_Str                                                 # message content

class List__Chat__Messages(Type_Safe__List):                           # Typed collection for messages
    expected_type = Schema__Chat__Message
