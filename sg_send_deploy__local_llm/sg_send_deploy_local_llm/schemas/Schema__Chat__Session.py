# ═══════════════════════════════════════════════════════════════════════════════
# Chat Session Schema — complete chat session stored as JSON
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                               import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Str                                import Safe_Str
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now   import Timestamp_Now
from osbot_utils.type_safe.primitives.domains.llm.safe_str.Safe_Str__LLM__Model_Id import Safe_Str__LLM__Model_Id
from sg_send_deploy_local_llm.schemas.types.Chat__Session_Id                       import Chat__Session_Id
from sg_send_deploy_local_llm.schemas.types.Enum__Chat__Session_Status             import Enum__Chat__Session_Status
from sg_send_deploy_local_llm.schemas.Schema__Chat__Message                        import List__Chat__Messages

class Schema__Chat__Session(Type_Safe):                                        # Complete chat session
    id         : Chat__Session_Id                                              # auto-generated 8-char hex
    title      : Safe_Str                                                      # auto-generated from first message
    model      : Safe_Str__LLM__Model_Id                                       # e.g. "gemma3:4b"
    status     : Enum__Chat__Session_Status = Enum__Chat__Session_Status.ACTIVE
    created_at : Timestamp_Now                                                 # epoch ms, auto-set
    updated_at : Timestamp_Now                                                 # epoch ms, updated on modify
    messages   : List__Chat__Messages                                          # ordered message history
