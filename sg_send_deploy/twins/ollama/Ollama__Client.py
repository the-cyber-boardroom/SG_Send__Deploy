import json

from osbot_utils.utils.Http import GET_json, POST_json


class Ollama__Client:
    """Client for Ollama HTTP API. Used by the operation class.
    In production, talks to localhost via SSH tunnel.
    In tests, replaced by Ollama__Surrogate."""

    def __init__(self, base_url: str = 'http://127.0.0.1:11434'):
        self.base_url = base_url

    def api_tags(self) -> dict:
        return GET_json(f'{self.base_url}/api/tags')

    def api_chat(self, model: str, messages: list) -> dict:
        payload = dict(model    = model    ,
                       messages = messages ,
                       stream   = False    )
        return POST_json(f'{self.base_url}/api/chat', data=payload)

    def api_generate(self, model: str, prompt: str) -> dict:
        payload = dict(model  = model  ,
                       prompt = prompt ,
                       stream = False  )
        return POST_json(f'{self.base_url}/api/generate', data=payload)

    def is_alive(self) -> bool:
        try:
            result = self.api_tags()
            return isinstance(result, dict) and 'models' in result
        except Exception:
            return False
