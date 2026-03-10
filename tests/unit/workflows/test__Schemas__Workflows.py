from unittest import TestCase

from sg_send_deploy.workflows.schemas.Schema__QA__Check        import Schema__QA__Check
from sg_send_deploy.workflows.schemas.Schema__QA__Result       import Schema__QA__Result
from sg_send_deploy.workflows.schemas.Schema__EC2__LLM__Request  import Schema__EC2__LLM__Request
from sg_send_deploy.workflows.schemas.Schema__EC2__LLM__Response import Schema__EC2__LLM__Response


class Test__Schema__QA__Check(TestCase):

    def test_defaults(self):
        check = Schema__QA__Check()
        assert check.check_id == ''
        assert check.prompt   == ''

    def test_set_values(self):
        check = Schema__QA__Check(check_id='c-1', prompt='check page')
        assert check.check_id == 'c-1'
        assert check.prompt   == 'check page'


class Test__Schema__QA__Result(TestCase):

    def test_defaults(self):
        result = Schema__QA__Result()
        assert result.check_id       == ''
        assert result.passed         is False
        assert result.tokens_per_sec == 0.0
        assert result.duration_ms    == 0

    def test_json(self):
        result = Schema__QA__Result(check_id='c-1', passed=True, duration_ms=150)
        data = result.json()
        assert data['check_id']    == 'c-1'
        assert data['passed']      is True
        assert data['duration_ms'] == 150


class Test__Schema__EC2__LLM__Request(TestCase):

    def test_defaults(self):
        req = Schema__EC2__LLM__Request()
        assert req.instance_type == 'c7g.xlarge'
        assert req.spot_instance is True
        assert req.model         == 'gemma3:4b'


class Test__Schema__EC2__LLM__Response(TestCase):

    def test_defaults(self):
        resp = Schema__EC2__LLM__Response()
        assert resp.success           is False
        assert resp.instance_id       == ''
        assert resp.boot_time_seconds == 0.0
        assert resp.error             == ''

    def test_json(self):
        resp = Schema__EC2__LLM__Response(success=True, instance_id='i-123')
        data = resp.json()
        assert data['success']     is True
        assert data['instance_id'] == 'i-123'
