from sg_send_deploy.ec2.providers.EC2_Provider import EC2_Provider

class EC2_Provider__AWS(EC2_Provider):

    def run_instances(self, instance_type: str = 't3.micro' ,
                            image_id     : str = ''         ,
                            key_name     : str = ''         ) -> dict:
        from osbot_aws.aws.ec2.EC2 import EC2
        ec2 = EC2()
        return ec2.instance_create(image_id      = image_id      ,
                                   instance_type = instance_type ,
                                   key_name      = key_name      )

    def describe_instance(self, instance_id: str) -> dict:
        from osbot_aws.aws.ec2.EC2 import EC2
        ec2 = EC2()
        return ec2.instance_details(instance_id=instance_id)

    def list_instances(self) -> list:
        from osbot_aws.aws.ec2.EC2 import EC2
        ec2 = EC2()
        return ec2.instances_details()

    def terminate_instance(self, instance_id: str) -> dict:
        from osbot_aws.aws.ec2.EC2 import EC2
        ec2 = EC2()
        return ec2.instance_terminate(instance_id=instance_id)

    def stop_instance(self, instance_id: str) -> dict:
        from osbot_aws.aws.ec2.EC2 import EC2
        ec2 = EC2()
        return ec2.instance_stop(instance_id=instance_id)

    def start_instance(self, instance_id: str) -> dict:
        from osbot_aws.aws.ec2.EC2 import EC2
        ec2 = EC2()
        return ec2.instance_start(instance_id=instance_id)
