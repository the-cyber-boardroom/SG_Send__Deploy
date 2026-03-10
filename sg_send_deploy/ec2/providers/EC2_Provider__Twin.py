from sg_send_deploy.ec2.providers.EC2_Provider           import EC2_Provider
from sg_send_deploy.twins.aws.ec2.Type__Twin__EC2__Fleet import Type__Twin__EC2__Fleet

class EC2_Provider__Twin(EC2_Provider):
    def __init__(self, fleet=None):
        self.fleet = fleet or Type__Twin__EC2__Fleet()

    def run_instances(self, instance_type: str = 't3.micro' ,
                            image_id     : str = ''         ,
                            key_name     : str = ''         ) -> dict:
        result = self.fleet.create_instance(instance_type = instance_type ,
                                            image_id      = image_id      ,
                                            key_name      = key_name      )
        return dict(instance_id = result.get('instance_id', ''))

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
