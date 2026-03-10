from unittest import TestCase

from sg_send_deploy.twins.ollama.Ollama__Surrogate import Ollama__Surrogate


class Test__Ollama__Surrogate(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.surrogate = Ollama__Surrogate()

    def test_is_alive(self):
        assert self.surrogate.is_alive() is True

    def test_api_tags(self):
        result = self.surrogate.api_tags()
        assert 'models' in result
        assert result['models'][0]['name'] == 'gemma3:4b'

    def test_api_chat__default_response(self):
        messages = [dict(role='user', content='check this page')]
        result = self.surrogate.api_chat(model='gemma3:4b', messages=messages)
        assert 'message' in result
        assert result['message']['role'] == 'assistant'

    def test_api_chat__custom_response(self):
        surrogate = Ollama__Surrogate()
        surrogate.add_response('find issues', dict(
            message=dict(role='assistant', content='{"findings": ["issue1"], "passed": false}'),
            total_duration=100_000_000,
            eval_count=50,
            eval_duration=100_000_000))

        messages = [dict(role='user', content='find issues')]
        result = surrogate.api_chat(model='gemma3:4b', messages=messages)
        assert '"issue1"' in result['message']['content']

    def test_api_generate__default_response(self):
        result = self.surrogate.api_generate(model='gemma3:4b', prompt='test prompt')
        assert 'response' in result

    def test_calls_tracked(self):
        surrogate = Ollama__Surrogate()
        surrogate.api_chat(model='gemma3:4b', messages=[dict(role='user', content='hi')])
        surrogate.api_generate(model='gemma3:4b', prompt='hello')
        assert len(surrogate.calls_made) == 2
