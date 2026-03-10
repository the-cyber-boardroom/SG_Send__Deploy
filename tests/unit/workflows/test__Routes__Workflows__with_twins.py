from unittest import TestCase

from fastapi                                                         import FastAPI
from fastapi.testclient                                              import TestClient
from sg_send_deploy.ec2.providers.EC2_Provider__Twin                 import EC2_Provider__Twin
from sg_send_deploy.twins.aws.ec2.Type__Twin__EC2__Fleet             import Type__Twin__EC2__Fleet
from sg_send_deploy.twins.ollama.Ollama__Surrogate                   import Ollama__Surrogate
from sg_send_deploy.utils.Audit_Trail                                import Audit_Trail
from sg_send_deploy.workflows.actions.Operation__EC2__Ephemeral__LLM import Operation__EC2__Ephemeral__LLM
from sg_send_deploy.workflows.routes.Routes__Workflows               import Routes__Workflows


def create_workflows_test_app():
    fleet     = Type__Twin__EC2__Fleet()
    provider  = EC2_Provider__Twin(fleet=fleet)
    surrogate = Ollama__Surrogate()
    trail     = Audit_Trail()
    operation = Operation__EC2__Ephemeral__LLM(
        ollama_client = surrogate ,
        ec2_provider  = provider  ,
        audit_trail   = trail     )

    app    = FastAPI()
    routes = Routes__Workflows(app=app, operation=operation)
    routes.setup()

    return TestClient(app), operation, surrogate, trail


class Test__Routes__Workflows__With_Twins(TestCase):

    def test_post_execute__no_checks(self):
        client, _, _, _ = create_workflows_test_app()

        response = client.post('/workflows/execute', params={
            'ami_id'        : 'ami-test-001' ,
            'instance_type' : 'c7g.xlarge'   ,
            'runner_ip'     : '1.2.3.4'      })

        assert response.status_code == 200
        data = response.json()
        assert data['success']     is True
        assert data['instance_id'] != ''
        assert data['results']     == []

    def test_post_execute__ollama_failure(self):
        fleet     = Type__Twin__EC2__Fleet()
        provider  = EC2_Provider__Twin(fleet=fleet)

        class FailingOllama(Ollama__Surrogate):
            def is_alive(self):
                return False

        operation = Operation__EC2__Ephemeral__LLM(
            ollama_client = FailingOllama() ,
            ec2_provider  = provider        )

        app    = FastAPI()
        routes = Routes__Workflows(app=app, operation=operation)
        routes.setup()
        client = TestClient(app)

        response = client.post('/workflows/execute', params={
            'ami_id': 'ami-test-001'})

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is False
        assert 'not responding' in data['error']
