import os
from unittest import TestCase

from fastapi                                            import FastAPI
from fastapi.testclient                                 import TestClient
from sg_send_deploy.ec2.providers.EC2_Provider__Twin    import EC2_Provider__Twin
from sg_send_deploy.server.routes.Routes__Status        import Routes__Status
from sg_send_deploy.twins.aws.ec2.Type__Twin__EC2__Fleet import Type__Twin__EC2__Fleet


def create_test_app():
    fleet    = Type__Twin__EC2__Fleet()
    provider = EC2_Provider__Twin(fleet=fleet)

    app    = FastAPI()
    routes = Routes__Status(app=app, ec2_provider=provider)
    routes.setup()

    return TestClient(app), fleet, provider


class Test__Routes__Status__With_Twins(TestCase):

    def test_status__no_instance_id_configured(self):
        client, _, _ = create_test_app()

        os.environ.pop('DEPLOY_INSTANCE_ID', None)

        response = client.get('/deploy/status')
        assert response.status_code == 200
        data = response.json()
        assert data['status']  == 'error'
        assert 'DEPLOY_INSTANCE_ID' in data['message']

    def test_status__instance_running(self):
        client, fleet, _ = create_test_app()

        result = fleet.create_instance(image_id='ami-deploy-001', instance_type='t3.micro')
        instance_id = result['instance_id']

        os.environ['DEPLOY_INSTANCE_ID'] = instance_id
        try:
            response = client.get('/deploy/status')
            assert response.status_code == 200
            data = response.json()
            assert data['status']      == 'running'
            assert data['instance_id'] == instance_id
            assert data['public_ip']   != ''
        finally:
            os.environ.pop('DEPLOY_INSTANCE_ID', None)

    def test_status__instance_stopped(self):
        client, fleet, _ = create_test_app()

        result = fleet.create_instance(image_id='ami-deploy-001', instance_type='t3.micro')
        instance_id = result['instance_id']
        fleet.stop_instance(instance_id)

        os.environ['DEPLOY_INSTANCE_ID'] = instance_id
        try:
            response = client.get('/deploy/status')
            data = response.json()
            assert data['status'] == 'stopped'
            assert data['healthy'] is False
        finally:
            os.environ.pop('DEPLOY_INSTANCE_ID', None)

    def test_status__healthy_false_when_no_real_server(self):
        client, fleet, _ = create_test_app()

        result = fleet.create_instance(image_id='ami-deploy-001', instance_type='t3.micro')
        instance_id = result['instance_id']

        os.environ['DEPLOY_INSTANCE_ID'] = instance_id
        try:
            response = client.get('/deploy/status')
            data = response.json()
            assert data['status']  == 'running'
            assert data['healthy'] is False
            assert 'endpoint' not in data
        finally:
            os.environ.pop('DEPLOY_INSTANCE_ID', None)
