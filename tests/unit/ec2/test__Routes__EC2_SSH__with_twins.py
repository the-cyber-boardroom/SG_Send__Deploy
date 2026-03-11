from unittest import TestCase

from fastapi.testclient import TestClient
from fastapi             import FastAPI

from sg_send_deploy.ec2.actions.Service__EC2_SSH    import Service__EC2_SSH
from sg_send_deploy.ec2.routes.Routes__EC2_SSH      import Routes__EC2_SSH
from sg_send_deploy.twins.ssh.SSH__Execute__Twin     import SSH__Execute__Twin


class Test__Routes__EC2_SSH__With_Twins(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ssh_twin    = SSH__Execute__Twin()
        cls.service_ssh = Service__EC2_SSH(ssh_execute=cls.ssh_twin)
        cls.app         = FastAPI()
        cls.routes      = Routes__EC2_SSH(app=cls.app, service_ssh=cls.service_ssh)
        cls.routes.setup()
        cls.client      = TestClient(cls.app)

    def setUp(self):
        self.ssh_twin.command_log.clear()

    # --- Connection ---

    def test_get_connection__not_configured(self):
        self.ssh_twin.ssh_host     = ''
        self.ssh_twin.ssh_key_file = ''
        self.ssh_twin.ssh_key_user = ''
        resp = self.client.get('/ssh/connection')
        assert resp.status_code == 200
        data = resp.json()
        assert data['ready'] is False

    def test_post_configure(self):
        resp = self.client.post('/ssh/configure', params={
            'host'     : '10.0.1.42',
            'key_file' : '/tmp/test.pem',
            'key_user' : 'ubuntu',
            'port'     : 22})
        assert resp.status_code == 200
        data = resp.json()
        assert data['status'] == 'configured'
        assert data['host']   == '10.0.1.42'

    def test_get_connection__after_configure(self):
        self.ssh_twin.ssh_host     = '10.0.1.42'
        self.ssh_twin.ssh_key_file = '/tmp/test.pem'
        self.ssh_twin.ssh_key_user = 'ubuntu'
        resp = self.client.get('/ssh/connection')
        data = resp.json()
        assert data['ready'] is True
        assert data['host']  == '10.0.1.42'

    # --- Execution ---

    def test_post_exec__not_configured(self):
        self.ssh_twin.ssh_host     = ''
        self.ssh_twin.ssh_key_file = ''
        self.ssh_twin.ssh_key_user = ''
        resp = self.client.post('/ssh/exec', params={'command': 'ls'})
        data = resp.json()
        assert data['status'] == 'error'
        assert 'not configured' in data['message']

    def test_post_exec__whoami(self):
        self.ssh_twin.ssh_host     = '10.0.1.42'
        self.ssh_twin.ssh_key_file = '/tmp/test.pem'
        self.ssh_twin.ssh_key_user = 'ubuntu'
        resp = self.client.post('/ssh/exec', params={'command': 'whoami'})
        data = resp.json()
        assert data['status']  == 'ok'
        assert data['stdout']  == 'ubuntu'
        assert data['command'] == 'whoami'

    def test_post_exec_commands(self):
        self.ssh_twin.ssh_host     = '10.0.1.42'
        self.ssh_twin.ssh_key_file = '/tmp/test.pem'
        self.ssh_twin.ssh_key_user = 'ubuntu'
        resp = self.client.post('/ssh/exec-commands',
                                params={'commands': 'whoami\nuname -a\nuptime'})
        data = resp.json()
        assert len(data) == 3
        assert data[0]['command'] == 'whoami'
        assert data[1]['command'] == 'uname -a'
        assert data[2]['command'] == 'uptime'

    # --- System info routes ---

    def test_get_whoami(self):
        self.ssh_twin.ssh_host     = '10.0.1.42'
        self.ssh_twin.ssh_key_file = '/tmp/test.pem'
        self.ssh_twin.ssh_key_user = 'ubuntu'
        resp = self.client.get('/ssh/whoami')
        assert resp.json()['stdout'] == 'ubuntu'

    def test_get_uname(self):
        self.ssh_twin.ssh_host     = '10.0.1.42'
        self.ssh_twin.ssh_key_file = '/tmp/test.pem'
        self.ssh_twin.ssh_key_user = 'ubuntu'
        resp = self.client.get('/ssh/uname')
        assert 'Linux' in resp.json()['stdout']

    def test_get_disk_space(self):
        self.ssh_twin.ssh_host     = '10.0.1.42'
        self.ssh_twin.ssh_key_file = '/tmp/test.pem'
        self.ssh_twin.ssh_key_user = 'ubuntu'
        resp = self.client.get('/ssh/disk-space')
        assert 'Filesystem' in resp.json()['stdout']

    # --- Filesystem ---

    def test_get_ls(self):
        self.ssh_twin.ssh_host     = '10.0.1.42'
        self.ssh_twin.ssh_key_file = '/tmp/test.pem'
        self.ssh_twin.ssh_key_user = 'ubuntu'
        resp = self.client.get('/ssh/ls', params={'path': '/home'})
        data = resp.json()
        assert data['status'] == 'ok'
        assert 'ls -la /home' in self.ssh_twin.command_log

    def test_get_cat(self):
        self.ssh_twin.ssh_host     = '10.0.1.42'
        self.ssh_twin.ssh_key_file = '/tmp/test.pem'
        self.ssh_twin.ssh_key_user = 'ubuntu'
        resp = self.client.get('/ssh/cat', params={'path': '/etc/hostname'})
        data = resp.json()
        assert data['status'] == 'ok'
        assert 'cat /etc/hostname' in self.ssh_twin.command_log

    def test_post_mkdir(self):
        self.ssh_twin.ssh_host     = '10.0.1.42'
        self.ssh_twin.ssh_key_file = '/tmp/test.pem'
        self.ssh_twin.ssh_key_user = 'ubuntu'
        resp = self.client.post('/ssh/mkdir', params={'path': '/opt/deploy'})
        data = resp.json()
        assert data['status'] == 'ok'
        assert 'mkdir -p /opt/deploy' in self.ssh_twin.command_log

    # --- Packages ---

    def test_post_apt_install(self):
        self.ssh_twin.ssh_host     = '10.0.1.42'
        self.ssh_twin.ssh_key_file = '/tmp/test.pem'
        self.ssh_twin.ssh_key_user = 'ubuntu'
        resp = self.client.post('/ssh/apt-install', params={'packages': 'nginx'})
        data = resp.json()
        assert data['status'] == 'ok'
        assert 'sudo apt-get install -y nginx' in self.ssh_twin.command_log

    def test_post_pip_install(self):
        self.ssh_twin.ssh_host     = '10.0.1.42'
        self.ssh_twin.ssh_key_file = '/tmp/test.pem'
        self.ssh_twin.ssh_key_user = 'ubuntu'
        resp = self.client.post('/ssh/pip-install', params={'packages': 'fastapi'})
        data = resp.json()
        assert data['status'] == 'ok'
        assert 'pip3 install fastapi' in self.ssh_twin.command_log

    # --- Services ---

    def test_post_systemctl(self):
        self.ssh_twin.ssh_host     = '10.0.1.42'
        self.ssh_twin.ssh_key_file = '/tmp/test.pem'
        self.ssh_twin.ssh_key_user = 'ubuntu'
        resp = self.client.post('/ssh/systemctl', params={'action': 'restart', 'service': 'nginx'})
        data = resp.json()
        assert data['status'] == 'ok'

    def test_get_service_status(self):
        self.ssh_twin.ssh_host     = '10.0.1.42'
        self.ssh_twin.ssh_key_file = '/tmp/test.pem'
        self.ssh_twin.ssh_key_user = 'ubuntu'
        resp = self.client.get('/ssh/service-status', params={'service': 'nginx'})
        data = resp.json()
        assert 'active (running)' in data['stdout']

    def test_get_service_logs(self):
        self.ssh_twin.ssh_host     = '10.0.1.42'
        self.ssh_twin.ssh_key_file = '/tmp/test.pem'
        self.ssh_twin.ssh_key_user = 'ubuntu'
        resp = self.client.get('/ssh/service-logs', params={'service': 'nginx'})
        data = resp.json()
        assert data['status'] == 'ok'

    # --- Command log tracks everything ---

    def test_command_log__tracks_all_commands(self):
        self.ssh_twin.ssh_host     = '10.0.1.42'
        self.ssh_twin.ssh_key_file = '/tmp/test.pem'
        self.ssh_twin.ssh_key_user = 'ubuntu'
        self.client.get('/ssh/whoami')
        self.client.get('/ssh/uname')
        self.client.get('/ssh/uptime')
        assert len(self.ssh_twin.command_log) == 3
        assert self.ssh_twin.command_log[0] == 'whoami'
        assert self.ssh_twin.command_log[1] == 'uname -a'
        assert self.ssh_twin.command_log[2] == 'uptime'
