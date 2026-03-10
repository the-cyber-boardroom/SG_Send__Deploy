import hashlib
import os

from datetime import datetime, timezone

from sg_send_deploy.twins.aws.ec2.Type__Twin__EC2__Instance       import Type__Twin__EC2__Instance
from sg_send_deploy.twins.aws.ec2.Type__Twin__EC2__Security_Group import Type__Twin__EC2__Security_Group

class Type__Twin__EC2__Fleet:
    def __init__(self):
        self.instances       = {}
        self.security_groups = {}
        self.key_pairs       = {}
        self.sg_ingress      = {}          # group_id -> list of (port, cidr_ip)

    def create_instance(self, **kwargs) -> dict:
        twin = Type__Twin__EC2__Instance()
        result = twin.execute('run_instances', **kwargs)
        instance_id = result.get('instance_id', '')
        self.instances[instance_id] = twin
        return result

    def terminate_instance(self, instance_id: str) -> dict:
        twin = self.instances.get(instance_id)
        if twin is None:
            return dict(status='error', message=f'Instance {instance_id} not found')
        return twin.execute('terminate_instances')

    def stop_instance(self, instance_id: str) -> dict:
        twin = self.instances.get(instance_id)
        if twin is None:
            return dict(status='error', message=f'Instance {instance_id} not found')
        return twin.execute('stop_instances')

    def start_instance(self, instance_id: str) -> dict:
        twin = self.instances.get(instance_id)
        if twin is None:
            return dict(status='error', message=f'Instance {instance_id} not found')
        return twin.execute('start_instances')

    def describe_instance(self, instance_id: str) -> dict:
        twin = self.instances.get(instance_id)
        if twin is None:
            return dict(status='error', message=f'Instance {instance_id} not found')
        return twin.execute('describe_instances')

    def list_instances(self, state_filter: str = '') -> list:
        results = []
        for instance_id, twin in self.instances.items():
            desc = twin.execute('describe_instances')
            if state_filter == '':
                results.append(desc)
            elif desc.get('state', {}).get('Name') == state_filter:
                results.append(desc)
        return results

    def running_count(self) -> int:
        return len(self.list_instances(state_filter='running'))

    def create_security_group(self, **kwargs) -> dict:
        twin = Type__Twin__EC2__Security_Group()
        result = twin.execute('create_security_group', **kwargs)
        group_id = result.get('group_id', '')
        self.security_groups[group_id] = twin
        return result

    def key_pair_create(self, key_name: str, target_folder: str = '/tmp') -> dict:
        seed       = f'{key_name}-{datetime.now(timezone.utc).isoformat()}'
        hash_val   = hashlib.md5(seed.encode()).hexdigest()[:17]
        key_pair_id = f'key-{hash_val}'
        key_path    = os.path.join(target_folder, f'{key_name}.pem')

        self.key_pairs[key_pair_id] = dict(key_pair_id = key_pair_id ,
                                           key_name    = key_name    ,
                                           key_path    = key_path    )
        return dict(key_pair_id = key_pair_id ,
                    key_name    = key_name     ,
                    key_path    = key_path     )

    def key_pair_delete(self, key_pair_id: str) -> dict:
        if key_pair_id in self.key_pairs:
            del self.key_pairs[key_pair_id]
            return dict(status='deleted', key_pair_id=key_pair_id)
        return dict(status='not_found', key_pair_id=key_pair_id)

    def security_group_authorize_ingress(self, group_id: str, port: int, cidr_ip: str) -> dict:
        rules = self.sg_ingress.setdefault(group_id, [])
        rules.append((port, cidr_ip))
        return dict(status='authorized', group_id=group_id, port=port, cidr_ip=cidr_ip)

    def security_group_revoke_ingress(self, group_id: str, port: int, cidr_ip: str) -> dict:
        rules = self.sg_ingress.get(group_id, [])
        entry = (port, cidr_ip)
        if entry in rules:
            rules.remove(entry)
            return dict(status='revoked', group_id=group_id)
        return dict(status='not_found', group_id=group_id)

    def wait_for_instance_running(self, instance_id: str, timeout: int = 120) -> dict:
        twin = self.instances.get(instance_id)
        if twin is None:
            return dict(status='error', message=f'Instance {instance_id} not found')
        return twin.execute('describe_instances')
