# ═══════════════════════════════════════════════════════════════════════════════
# Fast_API__Local_LLM — FastAPI app for local LLM chat
# ═══════════════════════════════════════════════════════════════════════════════

import os
from fastapi.responses                                                         import RedirectResponse
from fastapi.staticfiles                                                       import StaticFiles
from osbot_fast_api_serverless.fast_api.Serverless__Fast_API                    import Serverless__Fast_API
from osbot_fast_api_serverless.fast_api.routes.Routes__Info                     import Routes__Info
from sg_send_deploy_local_llm.fast_api.routes.Routes__Chat                     import Routes__Chat
from sg_send_deploy_local_llm.fast_api.routes.Routes__Models                   import Routes__Models
from sg_send_deploy_local_llm.fast_api.routes.Routes__Sessions                 import Routes__Sessions
from sg_send_deploy_local_llm.service.Service__Chat__Sessions                  import Service__Chat__Sessions
from sg_send_deploy_local_llm.service.Service__Ollama__Proxy                   import Service__Ollama__Proxy

STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(     # resolve to sg_send_deploy__local_llm/static
                 os.path.abspath(__file__)))), 'static')

class Fast_API__Local_LLM(Serverless__Fast_API):                               # Local LLM chat FastAPI app
    session_service : Service__Chat__Sessions = None
    ollama_proxy    : Service__Ollama__Proxy  = None

    def setup(self):
        self.config.enable_api_key = False                                     # no auth for local tool

        ollama_url = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')

        if self.ollama_proxy is None:
            self.ollama_proxy = Service__Ollama__Proxy(ollama_url=ollama_url)

        if self.session_service is None:
            self.session_service = Service__Chat__Sessions()

        result = super().setup()
        self.setup_static()
        return result

    def setup_routes(self):
        self.add_routes(Routes__Info)
        self.add_routes(Routes__Chat    , ollama_proxy    = self.ollama_proxy   )
        self.add_routes(Routes__Models  , ollama_proxy    = self.ollama_proxy   )
        self.add_routes(Routes__Sessions, session_service = self.session_service)

    def setup_static(self):                                                    # Mount static files + index redirect
        app = self.app()

        @app.get('/')
        def redirect_to_index():
            return RedirectResponse(url='/static/index.html')

        static_dir = os.environ.get('STATIC_DIR', STATIC_DIR)
        if os.path.isdir(static_dir):
            app.mount('/static', StaticFiles(directory=static_dir), name='static')
