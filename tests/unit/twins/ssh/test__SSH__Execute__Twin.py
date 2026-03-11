from unittest import TestCase

from sg_send_deploy.twins.ssh.SSH__Execute__Twin import SSH__Execute__Twin


class Test__SSH__Execute__Twin(TestCase):

    def setUp(self):
        self.twin = SSH__Execute__Twin()

    def test_initial_state__not_configured(self):
        assert self.twin.ssh_setup_ok() is False

    def test_configure__makes_setup_ok(self):
        self.twin.ssh_host     = '10.0.1.1'
        self.twin.ssh_key_file = '/tmp/key.pem'
        self.twin.ssh_key_user = 'ubuntu'
        assert self.twin.ssh_setup_ok() is True

    def test_execute_command__returns_dict(self):
        self.twin.ssh_host     = '10.0.1.1'
        self.twin.ssh_key_file = '/tmp/key.pem'
        self.twin.ssh_key_user = 'ubuntu'
        result = self.twin.execute_command('whoami')
        assert result['status']  == 'ok'
        assert result['stdout']  == 'ubuntu'
        assert result['stderr']  == ''
        assert result['command'] == 'whoami'

    def test_execute_command__logs_commands(self):
        self.twin.execute_command('cmd1')
        self.twin.execute_command('cmd2')
        assert self.twin.command_log == ['cmd1', 'cmd2']

    def test_execute_command__ls(self):
        result = self.twin.execute_command('ls -la /home')
        assert 'total' in result['stdout']

    def test_execute_command__cat(self):
        result = self.twin.execute_command('cat /etc/hostname')
        assert '/etc/hostname' in result['stdout']

    def test_execute_command__apt_install(self):
        result = self.twin.execute_command('sudo apt-get install -y nginx')
        assert result['stdout'] == 'Done'

    def test_execute_command__pip_install(self):
        result = self.twin.execute_command('pip3 install fastapi')
        assert 'fastapi' in result['stdout']

    def test_execute_command__systemctl_status(self):
        result = self.twin.execute_command('sudo systemctl status nginx')
        assert 'active (running)' in result['stdout']

    def test_exec__returns_stdout(self):
        result = self.twin.exec('whoami')
        assert result == 'ubuntu'
