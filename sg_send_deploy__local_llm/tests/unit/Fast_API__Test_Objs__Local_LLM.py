# ═══════════════════════════════════════════════════════════════════════════════
# Test infrastructure — shared test setup for FastAPI route tests
# ═══════════════════════════════════════════════════════════════════════════════

from osbot_utils.type_safe.Type_Safe                                           import Type_Safe
from sg_send_deploy_local_llm.fast_api.Fast_API__Local_LLM                     import Fast_API__Local_LLM
from sg_send_deploy_local_llm.service.Service__Chat__Sessions                  import Service__Chat__Sessions
from sg_send_deploy_local_llm.service.Service__Ollama__Proxy                   import Service__Ollama__Proxy

class Fast_API__Test_Objs__Local_LLM(Type_Safe):                               # Test singleton container
    fast_api        : Fast_API__Local_LLM = None
    fast_api__client: object              = None                                # TestClient

_test_objs = None                                                              # singleton for test session

def setup__fast_api__local_llm__test_objs():
    global _test_objs
    if _test_objs:
        return _test_objs

    session_service = Service__Chat__Sessions()                                # in-memory storage
    ollama_proxy    = Service__Ollama__Proxy()                                  # default localhost

    fast_api = Fast_API__Local_LLM(session_service = session_service,
                                   ollama_proxy    = ollama_proxy   )
    fast_api.setup()

    from fastapi.testclient import TestClient
    client = TestClient(fast_api.app())

    _test_objs = Fast_API__Test_Objs__Local_LLM(fast_api         = fast_api,
                                                 fast_api__client = client  )
    return _test_objs
