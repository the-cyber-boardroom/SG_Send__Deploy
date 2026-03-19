# ═══════════════════════════════════════════════════════════════════════════════
# Chat Request Schema — POST /api/chat request body
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                               import Type_Safe
from osbot_utils.type_safe.primitives.domains.llm.safe_str.Safe_Str__LLM__Model_Id import Safe_Str__LLM__Model_Id
from sg_send_deploy_local_llm.schemas.Schema__Chat__Message                        import List__Chat__Messages

class Schema__Chat__Request(Type_Safe):                                # POST /api/chat request body
    model    : Safe_Str__LLM__Model_Id                                 # target Ollama model
    messages : List__Chat__Messages                                    # conversation history
    stream   : bool = True                                             # always true for this UI
