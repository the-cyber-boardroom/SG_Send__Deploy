from osbot_utils.type_safe.Type_Safe import Type_Safe


class Ollama__Surrogate(Type_Safe):
    """In-memory twin of Ollama's HTTP API. Deterministic responses for known prompts.
    Used in unit tests — no real Ollama instance needed."""

    responses  : dict
    latency_ms : int  = 50
    calls_made : list
    model      : str  = 'gemma3:4b'

    def api_tags(self) -> dict:
        return dict(models=[dict(name=self.model, size='4.0 GB')])

    def api_chat(self, model: str, messages: list) -> dict:
        prompt_key = self._prompt_key(messages)
        self.calls_made.append(dict(model=model, messages=messages))

        if prompt_key in self.responses:
            return self.responses[prompt_key]

        return dict(message=dict(role='assistant',
                                 content='{"findings": [], "passed": true}'),
                    total_duration=self.latency_ms * 1_000_000,
                    eval_count=20,
                    eval_duration=self.latency_ms * 1_000_000)

    def api_generate(self, model: str, prompt: str) -> dict:
        self.calls_made.append(dict(model=model, prompt=prompt))

        if prompt in self.responses:
            return self.responses[prompt]

        return dict(response='{"findings": [], "passed": true}',
                    total_duration=self.latency_ms * 1_000_000,
                    eval_count=20,
                    eval_duration=self.latency_ms * 1_000_000)

    def is_alive(self) -> bool:
        return True

    def add_response(self, prompt_or_key: str, response: dict):
        self.responses[prompt_or_key] = response

    def _prompt_key(self, messages: list) -> str:
        if messages:
            return messages[-1].get('content', '')
        return ''
