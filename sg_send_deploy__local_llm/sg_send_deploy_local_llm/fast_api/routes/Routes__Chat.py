# ═══════════════════════════════════════════════════════════════════════════════
# Routes__Chat — POST /api/chat — streaming LLM proxy
# ═══════════════════════════════════════════════════════════════════════════════

from fastapi                                                                   import Request
from fastapi.responses                                                         import StreamingResponse
from osbot_fast_api.api.routes.Fast_API__Routes                                import Fast_API__Routes
from sg_send_deploy_local_llm.service.Service__Ollama__Proxy                   import Service__Ollama__Proxy

class Routes__Chat(Fast_API__Routes):                                          # POST /api/chat — streaming proxy
    tag          : str = 'api/chat'
    ollama_proxy : Service__Ollama__Proxy = None

    def setup_routes(self):                                                    # Register streaming route directly
        async def chat_endpoint(request: Request) -> StreamingResponse:
            body = await request.json()
            return StreamingResponse(self.ollama_proxy.stream_chat(body),
                                     media_type='application/x-ndjson')

        self.router.add_api_route(path     = '/chat'       ,
                                  endpoint = chat_endpoint ,
                                  methods  = ['POST']      ,
                                  tags     = [self.tag]     )
        return self
