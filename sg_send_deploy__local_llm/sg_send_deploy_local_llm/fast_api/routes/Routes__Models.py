# ═══════════════════════════════════════════════════════════════════════════════
# Routes__Models — GET /api/models — list Ollama models
# ═══════════════════════════════════════════════════════════════════════════════

import asyncio
from osbot_fast_api.api.routes.Fast_API__Routes                import Fast_API__Routes
from sg_send_deploy_local_llm.service.Service__Ollama__Proxy   import Service__Ollama__Proxy

class Routes__Models(Fast_API__Routes):                                        # GET /api/models
    tag          : str = 'api/models'
    ollama_proxy : Service__Ollama__Proxy = None

    def models(self) -> dict:                                                  # GET /api/models/models
        loop   = asyncio.new_event_loop()
        models = loop.run_until_complete(self.ollama_proxy.list_models())
        loop.close()
        return dict(models=models)

    def setup_routes(self):
        self.add_route_get(self.models)
        return self
