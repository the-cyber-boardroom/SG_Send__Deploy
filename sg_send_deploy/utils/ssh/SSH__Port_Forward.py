import subprocess

from osbot_utils.helpers.ssh.SSH__Execute import SSH__Execute


class SSH__Port_Forward:
    """Local helper that extends SSH__Execute with port forwarding.
    Uses subprocess.Popen (non-blocking) for long-running SSH tunnels.
    This will be moved to osbot-utils once confirmed working."""

    def __init__(self, ssh_execute: SSH__Execute = None):
        self.ssh_execute = ssh_execute or SSH__Execute()
        self._process    = None

    def start(self, local_port: int, remote_port: int,
              remote_host: str = '127.0.0.1') -> 'SSH__Port_Forward':
        if self._process is not None:
            self.stop()
        ssh_args  = self.ssh_execute.execute_ssh_args()
        ssh_args += ['-N']
        ssh_args += ['-L', f'{local_port}:{remote_host}:{remote_port}']
        ssh_args += [self.ssh_execute.execute_command_target_host()]
        self._process = subprocess.Popen(['ssh'] + ssh_args,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
        return self

    def stop(self):
        if self._process is not None:
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
            self._process = None

    def is_running(self) -> bool:
        return self._process is not None and self._process.poll() is None

    @property
    def pid(self) -> int:
        if self._process:
            return self._process.pid
        return 0

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.stop()
