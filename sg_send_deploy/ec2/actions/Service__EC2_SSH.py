from osbot_utils.helpers.ssh.SSH__Execute import SSH__Execute
from osbot_utils.helpers.ssh.SSH__Linux  import SSH__Linux
from osbot_utils.helpers.ssh.SCP         import SCP


class Service__EC2_SSH:
    """SSH operations against a target EC2 instance.

    In twin mode the ssh_execute is replaced with a fake that records commands."""

    def __init__(self, ssh_execute=None):
        self.ssh_execute = ssh_execute or SSH__Execute()

    def configure(self, host     : str ,
                        key_file : str ,
                        key_user : str = 'ubuntu',
                        port     : int = 22       ) -> dict:
        self.ssh_execute.ssh_host     = host
        self.ssh_execute.ssh_key_file = key_file
        self.ssh_execute.ssh_key_user = key_user
        self.ssh_execute.ssh_port     = port
        return dict(status = 'configured',
                    host   = host         ,
                    user   = key_user     ,
                    port   = port         )

    def connection_info(self) -> dict:
        return dict(host     = self.ssh_execute.ssh_host     ,
                    user     = self.ssh_execute.ssh_key_user ,
                    port     = self.ssh_execute.ssh_port     ,
                    key_file = self.ssh_execute.ssh_key_file ,
                    ready    = self.ssh_execute.ssh_setup_ok())

    def exec(self, command: str) -> dict:
        if not self.ssh_execute.ssh_setup_ok():
            return dict(status='error', message='SSH not configured')
        result = self.ssh_execute.execute_command(command)
        return dict(status  = result.get('status' , ''),
                    stdout  = result.get('stdout' , ''),
                    stderr  = result.get('stderr' , ''),
                    command = command                    )

    def exec_commands(self, commands: list) -> list:
        results = []
        for command in commands:
            results.append(self.exec(command))
        return results

    # --- Linux helpers (via SSH__Linux) ---

    def whoami(self) -> dict:
        return self.exec('whoami')

    def uname(self) -> dict:
        return self.exec('uname -a')

    def disk_space(self) -> dict:
        return self.exec('df -h')

    def memory_usage(self) -> dict:
        return self.exec('free -h')

    def uptime(self) -> dict:
        return self.exec('uptime')

    def processes(self) -> dict:
        return self.exec('ps aux')

    def ls(self, path: str = '/') -> dict:
        return self.exec(f'ls -la {path}')

    def cat(self, path: str) -> dict:
        return self.exec(f'cat {path}')

    def mkdir(self, path: str) -> dict:
        return self.exec(f'mkdir -p {path}')

    # --- Package management ---

    def apt_update(self) -> dict:
        return self.exec('sudo apt-get update -y')

    def apt_install(self, packages: str) -> dict:
        return self.exec(f'sudo apt-get install -y {packages}')

    def pip_install(self, packages: str) -> dict:
        return self.exec(f'pip3 install {packages}')

    def pip_list(self) -> dict:
        return self.exec('pip3 list')

    # --- Service management ---

    def systemctl(self, action: str, service: str) -> dict:
        return self.exec(f'sudo systemctl {action} {service}')

    def service_status(self, service: str) -> dict:
        return self.exec(f'sudo systemctl status {service}')

    def service_logs(self, service: str, lines: int = 100) -> dict:
        return self.exec(f'sudo journalctl -u {service} --no-pager -n {lines}')

    # --- File transfer (SCP) ---

    def upload_file(self, local_path: str, remote_path: str) -> dict:
        if not self.ssh_execute.ssh_setup_ok():
            return dict(status='error', message='SSH not configured')
        scp = SCP(ssh_host     = self.ssh_execute.ssh_host     ,
                  ssh_port     = self.ssh_execute.ssh_port     ,
                  ssh_key_file = self.ssh_execute.ssh_key_file ,
                  ssh_key_user = self.ssh_execute.ssh_key_user )
        stderr = scp.copy_file_to_host(local_path, remote_path)
        if stderr:
            return dict(status='error', message=stderr, remote_path=remote_path)
        return dict(status='uploaded', remote_path=remote_path)

    def download_file(self, remote_path: str, local_path: str) -> dict:
        if not self.ssh_execute.ssh_setup_ok():
            return dict(status='error', message='SSH not configured')
        scp = SCP(ssh_host     = self.ssh_execute.ssh_host     ,
                  ssh_port     = self.ssh_execute.ssh_port     ,
                  ssh_key_file = self.ssh_execute.ssh_key_file ,
                  ssh_key_user = self.ssh_execute.ssh_key_user )
        stderr = scp.copy_file_from_host(remote_path, local_path)
        if stderr:
            return dict(status='error', message=stderr, remote_path=remote_path)
        return dict(status='downloaded', local_path=local_path)
