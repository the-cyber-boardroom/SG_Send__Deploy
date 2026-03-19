# ═══════════════════════════════════════════════════════════════════════════════
# Service__Ollama__Proxy — streaming proxy to Ollama
# ═══════════════════════════════════════════════════════════════════════════════

import httpx
from typing                                                                    import AsyncIterator
from osbot_utils.type_safe.Type_Safe                                           import Type_Safe
from osbot_utils.utils.Json                                                    import json_loads

class Service__Ollama__Proxy(Type_Safe):                                       # Streaming proxy to Ollama
    ollama_url : str = 'http://localhost:11434'                                 # overridden by OLLAMA_HOST env var

    async def stream_chat(self, request_body: dict) -> AsyncIterator[bytes]:   # Stream proxy to Ollama /api/chat
        async with httpx.AsyncClient(timeout=300.0) as client:
            async with client.stream('POST',
                                     f'{self.ollama_url}/api/chat',
                                     json=request_body) as response:
                async for chunk in response.aiter_bytes():
                    yield chunk

    async def list_models(self) -> list:                                       # Returns raw model list from Ollama
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f'{self.ollama_url}/api/tags')
            data     = json_loads(response.text)
            return data.get('models', [])
