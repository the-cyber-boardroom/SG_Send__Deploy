from osbot_fast_api.api.routes.Fast_API__Routes import Fast_API__Routes

from sg_send_deploy.ec2.actions.Service__EC2_SSH import Service__EC2_SSH

TAG__ROUTES_SSH = 'ssh'


class Routes__EC2_SSH(Fast_API__Routes):
    tag         : str              = TAG__ROUTES_SSH
    service_ssh : Service__EC2_SSH

    # --- Connection management ---

    def configure(self, host     : str            ,           # POST /ssh/configure
                        key_file : str            ,
                        key_user : str = 'ubuntu' ,
                        port     : int = 22        ) -> dict:
        return self.service_ssh.configure(host=host, key_file=key_file, key_user=key_user, port=port)

    def connection(self) -> dict:                              # GET  /ssh/connection
        return self.service_ssh.connection_info()

    # --- Command execution ---

    def exec(self, command: str) -> dict:                      # POST /ssh/exec
        return self.service_ssh.exec(command)

    def exec_commands(self, commands: str) -> list:            # POST /ssh/exec-commands
        """Execute multiple commands. Pass commands separated by newlines."""
        cmd_list = [c.strip() for c in commands.split('\n') if c.strip()]
        return self.service_ssh.exec_commands(cmd_list)

    # --- System info ---

    def whoami(self) -> dict:                                  # GET  /ssh/whoami
        return self.service_ssh.whoami()

    def uname(self) -> dict:                                   # GET  /ssh/uname
        return self.service_ssh.uname()

    def disk_space(self) -> dict:                              # GET  /ssh/disk-space
        return self.service_ssh.disk_space()

    def memory_usage(self) -> dict:                            # GET  /ssh/memory-usage
        return self.service_ssh.memory_usage()

    def uptime(self) -> dict:                                  # GET  /ssh/uptime
        return self.service_ssh.uptime()

    def processes(self) -> dict:                               # GET  /ssh/processes
        return self.service_ssh.processes()

    # --- Filesystem ---

    def ls(self, path: str = '/') -> dict:                     # GET  /ssh/ls
        return self.service_ssh.ls(path)

    def cat(self, path: str) -> dict:                          # GET  /ssh/cat
        return self.service_ssh.cat(path)

    def mkdir(self, path: str) -> dict:                        # POST /ssh/mkdir
        return self.service_ssh.mkdir(path)

    # --- Package management ---

    def apt_update(self) -> dict:                              # POST /ssh/apt-update
        return self.service_ssh.apt_update()

    def apt_install(self, packages: str) -> dict:              # POST /ssh/apt-install
        return self.service_ssh.apt_install(packages)

    def pip_install(self, packages: str) -> dict:              # POST /ssh/pip-install
        return self.service_ssh.pip_install(packages)

    def pip_list(self) -> dict:                                # GET  /ssh/pip-list
        return self.service_ssh.pip_list()

    # --- Service management ---

    def systemctl(self, action: str, service: str) -> dict:    # POST /ssh/systemctl
        return self.service_ssh.systemctl(action, service)

    def service_status(self, service: str) -> dict:            # GET  /ssh/service-status
        return self.service_ssh.service_status(service)

    def service_logs(self, service: str,                       # GET  /ssh/service-logs
                     lines: int = 100) -> dict:
        return self.service_ssh.service_logs(service, lines)

    # --- File transfer ---

    def upload_file(self, local_path: str,                     # POST /ssh/upload-file
                          remote_path: str) -> dict:
        return self.service_ssh.upload_file(local_path, remote_path)

    def download_file(self, remote_path: str,                  # POST /ssh/download-file
                            local_path: str) -> dict:
        return self.service_ssh.download_file(remote_path, local_path)

    def setup_routes(self):
        # Connection
        self.add_route_post(self.configure     )
        self.add_route_get (self.connection     )

        # Execution
        self.add_route_post(self.exec           )
        self.add_route_post(self.exec_commands  )

        # System info
        self.add_route_get (self.whoami         )
        self.add_route_get (self.uname          )
        self.add_route_get (self.disk_space     )
        self.add_route_get (self.memory_usage   )
        self.add_route_get (self.uptime         )
        self.add_route_get (self.processes      )

        # Filesystem
        self.add_route_get (self.ls             )
        self.add_route_get (self.cat            )
        self.add_route_post(self.mkdir          )

        # Packages
        self.add_route_post(self.apt_update     )
        self.add_route_post(self.apt_install    )
        self.add_route_post(self.pip_install    )
        self.add_route_get (self.pip_list       )

        # Services
        self.add_route_post(self.systemctl      )
        self.add_route_get (self.service_status )
        self.add_route_get (self.service_logs   )

        # File transfer
        self.add_route_post(self.upload_file    )
        self.add_route_post(self.download_file  )
        return self
