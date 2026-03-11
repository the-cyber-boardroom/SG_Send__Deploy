class SSH__Execute__Twin:
    """In-memory twin of SSH__Execute for testing SSH routes without a real server.

    Records all commands and returns configurable responses."""

    def __init__(self):
        self.ssh_host            = ''
        self.ssh_port            = 22
        self.ssh_key_file        = ''
        self.ssh_key_user        = ''
        self.strict_host_check   = False
        self.command_log          = []
        self.default_responses    = {}
        self._setup_default_responses()

    def _setup_default_responses(self):
        self.default_responses = {
            'whoami'          : 'ubuntu'                                                         ,
            'uname -a'        : 'Linux ip-10-0-1-42 5.15.0-1052-aws x86_64 GNU/Linux'          ,
            'uptime'          : ' 14:32:01 up 2 days,  3:15,  1 user,  load average: 0.1, 0.2' ,
            'df -h'           : 'Filesystem  Size  Used Avail Use% Mounted on\n'
                                '/dev/root    30G   12G   18G  40% /'                            ,
            'free -h'         : '              total   used   free\n'
                                'Mem:          3.8Gi  1.2Gi  2.0Gi\n'
                                'Swap:            0B     0B     0B'                              ,
            'ps aux'          : 'USER  PID %CPU %MEM COMMAND\n'
                                'root    1  0.0  0.1 /sbin/init\n'
                                'ubuntu 42  0.2  1.5 python3 -m uvicorn'                        ,
            'pip3 list'       : 'Package    Version\n'
                                '---------- -------\n'
                                'fastapi    0.104.1\n'
                                'uvicorn    0.24.0'                                              ,
        }

    def set_response(self, command: str, stdout: str, stderr: str = '', status: str = 'ok'):
        self.default_responses[command] = stdout

    def ssh_setup_ok(self):
        return bool(self.ssh_host and self.ssh_key_file and self.ssh_key_user)

    def ssh_not__setup_ok(self):
        return not self.ssh_setup_ok()

    def execute_command(self, command: str) -> dict:
        self.command_log.append(command)

        stdout = ''
        for prefix, response in self.default_responses.items():
            if command.startswith(prefix) or command == prefix:
                stdout = response
                break

        if command.startswith('ls -la'):
            path = command.replace('ls -la', '').strip() or '/'
            stdout = (f'total 8\n'
                      f'drwxr-xr-x  4 ubuntu ubuntu 4096 Mar 10 12:00 .\n'
                      f'drwxr-xr-x  3 root   root   4096 Mar 10 12:00 ..\n'
                      f'-rw-r--r--  1 ubuntu ubuntu  256 Mar 10 12:00 README.md')

        if command.startswith('cat '):
            path = command.replace('cat ', '').strip()
            stdout = f'# contents of {path}'

        if command.startswith('mkdir -p'):
            stdout = ''

        if command.startswith('sudo apt-get'):
            stdout = 'Done'

        if command.startswith('pip3 install'):
            pkg = command.replace('pip3 install ', '')
            stdout = f'Successfully installed {pkg}'

        if command.startswith('sudo systemctl status'):
            service = command.split()[-1]
            stdout = f'{service}.service - {service}\n   Active: active (running)'

        elif command.startswith('sudo systemctl'):
            parts = command.split()
            if len(parts) >= 4:
                action  = parts[2]
                service = parts[3]
                stdout = f'{service}: {action} ok'

        if command.startswith('sudo journalctl'):
            stdout = 'Mar 10 12:00:00 systemd[1]: Starting service...\nMar 10 12:00:01 systemd[1]: Started.'

        return dict(status = 'ok'    ,
                    stdout = stdout   ,
                    stderr = ''       ,
                    command = command  )

    def execute_command__return_stdout(self, command: str) -> str:
        return self.execute_command(command).get('stdout', '')

    def exec(self, command: str) -> str:
        return self.execute_command__return_stdout(command)

    def execute_ssh_args(self):
        return []

    def execute_command_target_host(self):
        return f'{self.ssh_key_user}@{self.ssh_host}'
