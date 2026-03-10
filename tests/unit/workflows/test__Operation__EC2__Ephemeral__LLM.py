from unittest import TestCase

from sg_send_deploy.ec2.providers.EC2_Provider__Twin               import EC2_Provider__Twin
from sg_send_deploy.twins.aws.ec2.Type__Twin__EC2__Fleet           import Type__Twin__EC2__Fleet
from sg_send_deploy.twins.ollama.Ollama__Surrogate                 import Ollama__Surrogate
from sg_send_deploy.utils.Audit_Trail                              import Audit_Trail
from sg_send_deploy.workflows.actions.Operation__EC2__Ephemeral__LLM import Operation__EC2__Ephemeral__LLM


SG_ID = 'sg-test-001'


def create_test_operation():
    fleet     = Type__Twin__EC2__Fleet()
    provider  = EC2_Provider__Twin(fleet=fleet)
    surrogate = Ollama__Surrogate()
    trail     = Audit_Trail()
    operation = Operation__EC2__Ephemeral__LLM(
        ollama_client      = surrogate ,
        ec2_provider       = provider  ,
        audit_trail        = trail     ,
        security_group_id  = SG_ID     )
    return operation, fleet, surrogate, trail


class Test__Operation__EC2__Ephemeral__LLM(TestCase):

    def test_execute__no_checks(self):
        operation, fleet, _, _ = create_test_operation()

        result = operation.execute(
            ami_id        = 'ami-test-001' ,
            instance_type = 'c7g.xlarge'   ,
            runner_ip     = '1.2.3.4'      ,
            admin         = 'test-admin'   )

        assert result['success']       is True
        assert result['instance_id']   != ''
        assert result['instance_type'] == 'c7g.xlarge'
        assert result['results']       == []

    def test_execute__with_checks(self):
        operation, _, surrogate, _ = create_test_operation()

        checks = [
            dict(check_id='check-1', prompt='check for untranslated strings'),
            dict(check_id='check-2', prompt='check for text overflow')        ]

        result = operation.execute(
            ami_id    = 'ami-test-001' ,
            model     = 'gemma3:4b'   ,
            checks    = checks        ,
            admin     = 'test-admin'  )

        assert result['success'] is True
        assert len(result['results']) == 2
        assert result['results'][0]['check_id'] == 'check-1'
        assert result['results'][1]['check_id'] == 'check-2'

    def test_execute__custom_surrogate_response(self):
        operation, _, surrogate, _ = create_test_operation()

        surrogate.add_response('find issues in locale page', dict(
            message=dict(role='assistant',
                         content='{"findings": ["untranslated: Welcome"], "passed": false}'),
            total_duration=200_000_000,
            eval_count=30,
            eval_duration=100_000_000))

        checks = [dict(check_id='locale-1', prompt='find issues in locale page')]

        result = operation.execute(
            ami_id = 'ami-test-001' ,
            checks = checks         )

        assert result['success'] is True
        assert len(result['results']) == 1
        r = result['results'][0]
        assert r['passed']   is False
        assert 'untranslated' in r['findings'][0]

    def test_execute__audit_logged(self):
        operation, _, _, trail = create_test_operation()

        operation.execute(
            ami_id = 'ami-test-001' ,
            admin  = 'qa-runner'    )

        entries = trail.get_entries()
        assert len(entries) >= 1
        assert entries[-1].action == 'EC2_LLM_EXECUTE'
        assert entries[-1].admin  == 'qa-runner'

    def test_execute__instance_cleaned_up(self):
        operation, fleet, _, _ = create_test_operation()

        operation.execute(ami_id='ami-test-001')

        running = fleet.list_instances(state_filter='running')
        assert len(running) == 0

    def test_execute__key_pair_cleaned_up(self):
        operation, fleet, _, _ = create_test_operation()

        operation.execute(ami_id='ami-test-001', runner_ip='1.2.3.4')

        assert len(fleet.key_pairs) == 0

    def test_execute__sg_ingress_cleaned_up(self):
        operation, fleet, _, _ = create_test_operation()

        operation.execute(ami_id='ami-test-001', runner_ip='1.2.3.4')

        rules = fleet.sg_ingress.get(SG_ID, [])
        assert len(rules) == 0

    def test_execute__ephemeral_key_pair_created(self):
        fleet     = Type__Twin__EC2__Fleet()
        provider  = EC2_Provider__Twin(fleet=fleet)
        surrogate = Ollama__Surrogate()

        class TrackingOperation(Operation__EC2__Ephemeral__LLM):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.captured_key_pair_id = ''

            def _verify_ollama(self, model: str):
                self.captured_key_pair_id = self.key_pair_id
                super()._verify_ollama(model=model)

        operation = TrackingOperation(
            ollama_client     = surrogate ,
            ec2_provider      = provider  ,
            security_group_id = SG_ID     )

        operation.execute(ami_id='ami-test-001', runner_ip='1.2.3.4')

        assert operation.captured_key_pair_id != ''
        assert operation.captured_key_pair_id.startswith('key-')

    def test_execute__handles_ollama_error(self):
        fleet     = Type__Twin__EC2__Fleet()
        provider  = EC2_Provider__Twin(fleet=fleet)
        surrogate = Ollama__Surrogate()
        trail     = Audit_Trail()

        class FailingOllama(Ollama__Surrogate):
            def is_alive(self):
                return False

        operation = Operation__EC2__Ephemeral__LLM(
            ollama_client     = FailingOllama() ,
            ec2_provider      = provider        ,
            audit_trail       = trail           ,
            security_group_id = SG_ID           )

        result = operation.execute(ami_id='ami-test-001')

        assert result['success'] is False
        assert 'not responding' in result['error']

        entries = trail.get_entries()
        assert entries[-1].action == 'EC2_LLM_EXECUTE_FAILED'

    def test_execute__cleanup_after_error(self):
        fleet     = Type__Twin__EC2__Fleet()
        provider  = EC2_Provider__Twin(fleet=fleet)

        class FailingOllama(Ollama__Surrogate):
            def is_alive(self):
                return False

        operation = Operation__EC2__Ephemeral__LLM(
            ollama_client     = FailingOllama() ,
            ec2_provider      = provider        ,
            security_group_id = SG_ID           )

        operation.execute(ami_id='ami-test-001', runner_ip='10.0.0.1')

        assert len(fleet.key_pairs) == 0
        assert len(fleet.sg_ingress.get(SG_ID, [])) == 0
        running = fleet.list_instances(state_filter='running')
        assert len(running) == 0

    def test_execute__boot_time_tracked(self):
        operation, _, _, _ = create_test_operation()

        result = operation.execute(ami_id='ami-test-001')

        assert result['boot_time_seconds'] >= 0.0
        assert result['total_duration_ms'] >= 0
