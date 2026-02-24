from sg_send_deploy.twins.aws.ec2.Type__Twin__EC2__Instance       import Type__Twin__EC2__Instance
from sg_send_deploy.twins.aws.ec2.Type__Twin__EC2__Security_Group import Type__Twin__EC2__Security_Group

class Type__Twin__EC2__Fleet:
    def __init__(self):
        self.instances       = {}
        self.security_groups = {}

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
