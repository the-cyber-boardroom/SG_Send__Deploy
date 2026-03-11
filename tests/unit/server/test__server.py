import os
from unittest import TestCase

from fastapi.testclient import TestClient

from sg_send_deploy.server.server import create_app

TEST_API_KEY_NAME  = 'test-api-key'
TEST_API_KEY_VALUE = 'test-secret-value'


class Test__Server(TestCase):

    @classmethod
    def setUpClass(cls):
        os.environ['FAST_API__AUTH__API_KEY__NAME' ] = TEST_API_KEY_NAME
        os.environ['FAST_API__AUTH__API_KEY__VALUE'] = TEST_API_KEY_VALUE

    @classmethod
    def tearDownClass(cls):
        os.environ.pop('FAST_API__AUTH__API_KEY__NAME' , None)
        os.environ.pop('FAST_API__AUTH__API_KEY__VALUE', None)

    def auth_headers(self):
        return {TEST_API_KEY_NAME: TEST_API_KEY_VALUE}

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
        resp = client.get('/ec2/instances', headers=self.auth_headers())
        assert resp.status_code == 200
        assert resp.json() == []

        # Deploy status route works
        os.environ.pop('DEPLOY_INSTANCE_ID', None)
        resp = client.get('/deploy/status', headers=self.auth_headers())
        assert resp.status_code == 200
        assert resp.json()['status'] == 'error'

    def test_create_app__twin_mode_create_and_list(self):
        os.environ.pop('USE_AWS_PROVIDER', None)
        app    = create_app()
        client = TestClient(app)

        # Create an instance
        resp = client.post('/ec2/create-instance', params={
            'instance_type': 't3.micro',
            'image_id': 'ami-test-001'}, headers=self.auth_headers())
        assert resp.status_code == 200
        data = resp.json()
        assert data['status'] == 'created'

        # List should have 1
        resp = client.get('/ec2/instances', headers=self.auth_headers())
        assert len(resp.json()) == 1

    def test_create_app__auth_rejects_bad_key(self):
        os.environ.pop('USE_AWS_PROVIDER', None)
        app    = create_app()
        client = TestClient(app)

        # No key → 401
        resp = client.get('/ec2/instances')
        assert resp.status_code == 401

        # Wrong key → 401
        resp = client.get('/ec2/instances', headers={TEST_API_KEY_NAME: 'wrong-value'})
        assert resp.status_code == 401

    def test_create_app__ssh_routes_available(self):
        os.environ.pop('USE_AWS_PROVIDER', None)
        app    = create_app()
        client = TestClient(app)
        headers = self.auth_headers()

        # SSH connection route works
        resp = client.get('/ssh/connection', headers=headers)
        assert resp.status_code == 200
        assert resp.json()['ready'] is False

        # Configure SSH
        resp = client.post('/ssh/configure', params={
            'host': '10.0.1.42', 'key_file': '/tmp/key.pem'}, headers=headers)
        assert resp.json()['status'] == 'configured'

        # Exec whoami via twin
        resp = client.post('/ssh/exec', params={'command': 'whoami'}, headers=headers)
        assert resp.json()['stdout'] == 'ubuntu'
