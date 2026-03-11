from sg_send_deploy.ec2.providers.EC2_Provider           import EC2_Provider
from sg_send_deploy.twins.aws.ec2.Type__Twin__EC2__Fleet import Type__Twin__EC2__Fleet

class EC2_Provider__Twin(EC2_Provider):
    def __init__(self, fleet=None):
        self.fleet = fleet or Type__Twin__EC2__Fleet()

    def run_instances(self, instance_type    : str  = 't3.micro' ,
                            image_id         : str  = ''         ,
                            key_name         : str  = ''         ,
                            security_group_id: str  = ''         ,
                            spot_instance    : bool = False       ,
                            tags             : dict = None        ) -> dict:
        result = self.fleet.create_instance(instance_type    = instance_type    ,
                                            image_id         = image_id         ,
                                            key_name         = key_name         ,
                                            security_group_id= security_group_id)
        return dict(instance_id = result.get('instance_id', ''),
                    public_ip   = result.get('public_ip'  , ''))

    def describe_instance(self, instance_id: str) -> dict:
        return self.fleet.describe_instance(instance_id=instance_id)

    def list_instances(self) -> list:
        return self.fleet.list_instances()

    def terminate_instance(self, instance_id: str) -> dict:
        return self.fleet.terminate_instance(instance_id=instance_id)

    def stop_instance(self, instance_id: str) -> dict:
        return self.fleet.stop_instance(instance_id=instance_id)

    def start_instance(self, instance_id: str) -> dict:
        return self.fleet.start_instance(instance_id=instance_id)

    def key_pair_create(self, key_name: str, target_folder: str = '/tmp') -> dict:
        return self.fleet.key_pair_create(key_name=key_name, target_folder=target_folder)

    def key_pair_delete(self, key_pair_id: str) -> dict:
        return self.fleet.key_pair_delete(key_pair_id=key_pair_id)

    def key_pairs_list(self) -> list:
        return self.fleet.key_pairs_list() if hasattr(self.fleet, 'key_pairs_list') else []

    def security_group_create(self, group_name: str, description: str, vpc_id: str = '') -> dict:
        if hasattr(self.fleet, 'security_group_create'):
            return self.fleet.security_group_create(group_name=group_name, description=description, vpc_id=vpc_id)
        return dict(status='ok', security_group_id='sg-twin-mock', group_name=group_name)

    def security_group_delete(self, group_id: str) -> dict:
        if hasattr(self.fleet, 'security_group_delete'):
            return self.fleet.security_group_delete(group_id=group_id)
        return dict(status='deleted', group_id=group_id)

    def security_groups_list(self) -> list:
        return self.fleet.security_groups_list() if hasattr(self.fleet, 'security_groups_list') else []

    def security_group_authorize_ingress(self, group_id: str, port: int, cidr_ip: str) -> dict:
        return self.fleet.security_group_authorize_ingress(group_id=group_id, port=port, cidr_ip=cidr_ip)

    def security_group_revoke_ingress(self, group_id: str, port: int, cidr_ip: str) -> dict:
        return self.fleet.security_group_revoke_ingress(group_id=group_id, port=port, cidr_ip=cidr_ip)

    def wait_for_instance_running(self, instance_id: str, timeout: int = 120) -> dict:
        return self.fleet.wait_for_instance_running(instance_id=instance_id, timeout=timeout)
