class EC2_Provider:

    def run_instances(self, instance_type    : str  = 't3.micro'  ,
                            image_id         : str  = ''          ,
                            key_name         : str  = ''          ,
                            security_group_id: str  = ''          ,
                            spot_instance    : bool = False       ,
                            tags             : dict = None        ) -> dict:
        raise NotImplementedError()

    def describe_instance(self, instance_id: str) -> dict:
        raise NotImplementedError()

    def list_instances(self) -> list:
        raise NotImplementedError()

    def terminate_instance(self, instance_id: str) -> dict:
        raise NotImplementedError()

    def stop_instance(self, instance_id: str) -> dict:
        raise NotImplementedError()

    def start_instance(self, instance_id: str) -> dict:
        raise NotImplementedError()

    def key_pair_create(self, key_name: str, target_folder: str = '/tmp') -> dict:
        raise NotImplementedError()

    def key_pair_delete(self, key_pair_id: str) -> dict:
        raise NotImplementedError()

    def key_pairs_list(self) -> list:
        raise NotImplementedError()

    def security_group_create(self, group_name: str, description: str, vpc_id: str = '') -> dict:
        raise NotImplementedError()

    def security_group_delete(self, group_id: str) -> dict:
        raise NotImplementedError()

    def security_groups_list(self) -> list:
        raise NotImplementedError()

    def security_group_authorize_ingress(self, group_id: str, port: int, cidr_ip: str) -> dict:
        raise NotImplementedError()

    def security_group_revoke_ingress(self, group_id: str, port: int, cidr_ip: str) -> dict:
        raise NotImplementedError()

    def wait_for_instance_running(self, instance_id: str, timeout: int = 120) -> dict:
        raise NotImplementedError()
