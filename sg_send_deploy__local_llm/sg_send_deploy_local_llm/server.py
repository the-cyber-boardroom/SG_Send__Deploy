# ═══════════════════════════════════════════════════════════════════════════════
# Server entry point — uvicorn target
# ═══════════════════════════════════════════════════════════════════════════════

from sg_send_deploy_local_llm.fast_api.Fast_API__Local_LLM import Fast_API__Local_LLM

fast_api = Fast_API__Local_LLM()
fast_api.setup()
app = fast_api.app()
