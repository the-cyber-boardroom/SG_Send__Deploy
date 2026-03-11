import os
from unittest import TestCase

from fastapi.testclient import TestClient

from sg_send_deploy.server.server import create_app


class Test__Server(TestCase):

    def test_create_app__returns_fastapi_app(self):
        os.environ.pop('USE_AWS_PROVIDER', None)
        app = create_app()
        assert app is not None
        assert hasattr(app, 'routes')

    def test_create_app__twin_mode_has_routes(self):
        os.environ.pop('USE_AWS_PROVIDER', None)
        app    = create_app()
        client = TestClient(app)

        # EC2 routes work
        resp = client.get('/ec2/instances')
        assert resp.status_code == 200
        assert resp.json() == []

        # Deploy status route works
        os.environ.pop('DEPLOY_INSTANCE_ID', None)
        resp = client.get('/deploy/status')
        assert resp.status_code == 200
        assert resp.json()['status'] == 'error'

    def test_create_app__twin_mode_create_and_list(self):
        os.environ.pop('USE_AWS_PROVIDER', None)
        app    = create_app()
        client = TestClient(app)

        # Create an instance
        resp = client.post('/ec2/create-instance', params={
            'instance_type': 't3.micro',
            'image_id': 'ami-test-001'})
        assert resp.status_code == 200
        data = resp.json()
        assert data['status'] == 'created'

        # List should have 1
        resp = client.get('/ec2/instances')
        assert len(resp.json()) == 1
