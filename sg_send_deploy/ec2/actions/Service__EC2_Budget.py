from sg_send_deploy.ec2.schemas.EC2_Budget_Config import EC2_Budget_Config


class Service__EC2_Budget:
    def __init__(self, config=None):
        self.config = config or EC2_Budget_Config()

    def check_instance_limit(self, current_count: int) -> dict:
        allowed = current_count < self.config.max_instances
        return dict(
            allowed       = allowed                  ,
            current_count = current_count            ,
            max_instances = self.config.max_instances ,
            message       = '' if allowed else f'Instance limit reached ({self.config.max_instances})')

    def check_instance_type(self, instance_type: str) -> dict:
        allowed_types = self.config.allowed_types()
        allowed = instance_type in allowed_types
        return dict(
            allowed        = allowed         ,
            instance_type  = instance_type   ,
            allowed_types  = allowed_types   ,
            message        = '' if allowed else f'Instance type {instance_type} not allowed. Use: {allowed_types}')

    def check_can_create(self, current_count: int, instance_type: str = 't3.micro') -> dict:
        limit_check = self.check_instance_limit(current_count)
        if not limit_check['allowed']:
            return limit_check

        type_check = self.check_instance_type(instance_type)
        if not type_check['allowed']:
            return type_check

        return dict(allowed=True, message='')
