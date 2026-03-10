from unittest import TestCase

from sg_send_deploy.utils.ssh.SSH__Port_Forward import SSH__Port_Forward
from osbot_utils.helpers.ssh.SSH__Execute       import SSH__Execute


class Test__SSH__Port_Forward(TestCase):

    def test_init__defaults(self):
        pf = SSH__Port_Forward()
        assert pf._process    is None
        assert pf.is_running() is False
        assert pf.pid          == 0

    def test_init__with_ssh_execute(self):
        ssh_exec = SSH__Execute()
        ssh_exec.ssh_host     = '10.0.0.1'
        ssh_exec.ssh_key_file = '/tmp/test.pem'
        ssh_exec.ssh_key_user = 'ubuntu'
        pf = SSH__Port_Forward(ssh_execute=ssh_exec)
        assert pf.ssh_execute.ssh_host == '10.0.0.1'

    def test_context_manager(self):
        with SSH__Port_Forward() as pf:
            assert pf._process is None
