from sg_send_deploy.ec2.actions.Service__EC2_Budget import Service__EC2_Budget
from sg_send_deploy.ec2.schemas.EC2_Instance_Info   import EC2_Instance_Info
from sg_send_deploy.utils.Audit_Trail               import Audit_Trail


class Service__EC2_Instances:
    def __init__(self, budget_service=None, audit_trail=None):
        self.budget_service = budget_service or Service__EC2_Budget()
        self.audit_trail    = audit_trail    or Audit_Trail()

    def create(self, instance_type: str = 't3.micro',
                     data_room_id : str = ''         ,
                     image_id     : str = ''         ,
                     key_name     : str = ''         ,
                     admin        : str = ''         ) -> dict:
        # Budget check before creating
        running = self.list_running()
        budget_check = self.budget_service.check_can_create(
            current_count = len(running)  ,
            instance_type = instance_type )
        if not budget_check['allowed']:
            return dict(status='error', message=budget_check['message'])

        # Create via osbot-aws
        try:
            from osbot_aws.aws.ec2.EC2 import EC2
            ec2 = EC2()
            result = ec2.instance_create(image_id      = image_id      ,
                                         instance_type = instance_type ,
                                         key_name      = key_name      )
            instance_id = result.get('instance_id', '')

            # Audit log
            self.audit_trail.record(
                action  = 'EC2_CREATE'                                            ,
                admin   = admin                                                   ,
                details = dict(instance_id   = instance_id                        ,
                               instance_type = instance_type                      ,
                               data_room_id  = data_room_id                       ,
                               image_id      = image_id                           ))

            return dict(status       = 'created'      ,
                        instance_id  = instance_id     ,
                        instance_type= instance_type   ,
                        data_room_id = data_room_id    )

        except Exception as e:
            self.audit_trail.record(
                action  = 'EC2_CREATE_FAILED'                 ,
                admin   = admin                               ,
                details = dict(error         = str(e)         ,
                               instance_type = instance_type  ,
                               data_room_id  = data_room_id   ))
            return dict(status='error', message=str(e))

    def list_running(self, admin: str = '') -> list:
        try:
            from osbot_aws.aws.ec2.EC2 import EC2
            ec2 = EC2()
            instances = ec2.instances_details()
            running = []
            for instance in instances:
                state = instance.get('state', {})
                if isinstance(state, dict):
                    state_name = state.get('Name', '')
                else:
                    state_name = str(state)
                if state_name in ('running', 'pending'):
                    info = EC2_Instance_Info(
                        instance_id   = instance.get('instance_id'  , ''),
                        status        = state_name                       ,
                        public_ip     = instance.get('public_ip'    , ''),
                        private_ip    = instance.get('private_ip'   , ''),
                        instance_type = instance.get('instance_type', ''),
                        ami_id        = instance.get('image_id'     , ''),
                        key_name      = instance.get('key_name'     , ''))
                    running.append(info.json())
            return running
        except Exception as e:
            return []

    def get_instance(self, instance_id: str, admin: str = '') -> dict:
        try:
            from osbot_aws.aws.ec2.EC2 import EC2
            ec2 = EC2()
            details = ec2.instance_details(instance_id=instance_id)
            if details:
                state = details.get('state', {})
                if isinstance(state, dict):
                    state_name = state.get('Name', '')
                else:
                    state_name = str(state)
                return dict(
                    status        = 'ok'                                    ,
                    instance_id   = details.get('instance_id'  , '')        ,
                    state         = state_name                              ,
                    public_ip     = details.get('public_ip'    , '')        ,
                    private_ip    = details.get('private_ip'   , '')        ,
                    instance_type = details.get('instance_type', '')        ,
                    ami_id        = details.get('image_id'     , '')        )
            return dict(status='error', message=f'Instance {instance_id} not found')
        except Exception as e:
            return dict(status='error', message=str(e))

    def terminate(self, instance_id: str, admin: str = '') -> dict:
        try:
            from osbot_aws.aws.ec2.EC2 import EC2
            ec2 = EC2()
            result = ec2.instance_terminate(instance_id=instance_id)

            self.audit_trail.record(
                action  = 'EC2_TERMINATE'                               ,
                admin   = admin                                         ,
                details = dict(instance_id = instance_id                ))

            return dict(status      = 'terminated'   ,
                        instance_id = instance_id    )

        except Exception as e:
            self.audit_trail.record(
                action  = 'EC2_TERMINATE_FAILED'                        ,
                admin   = admin                                         ,
                details = dict(instance_id = instance_id                ,
                               error       = str(e)                     ))
            return dict(status='error', message=str(e))

    def stop(self, instance_id: str, admin: str = '') -> dict:
        try:
            from osbot_aws.aws.ec2.EC2 import EC2
            ec2 = EC2()
            result = ec2.instance_stop(instance_id=instance_id)

            self.audit_trail.record(
                action  = 'EC2_STOP'                                    ,
                admin   = admin                                         ,
                details = dict(instance_id = instance_id                ))

            return dict(status      = 'stopping'     ,
                        instance_id = instance_id    )

        except Exception as e:
            return dict(status='error', message=str(e))

    def start(self, instance_id: str, admin: str = '') -> dict:
        try:
            from osbot_aws.aws.ec2.EC2 import EC2
            ec2 = EC2()

            # Budget check before starting
            running = self.list_running()
            budget_check = self.budget_service.check_instance_limit(len(running))
            if not budget_check['allowed']:
                return dict(status='error', message=budget_check['message'])

            result = ec2.instance_start(instance_id=instance_id)

            self.audit_trail.record(
                action  = 'EC2_START'                                   ,
                admin   = admin                                         ,
                details = dict(instance_id = instance_id                ))

            return dict(status      = 'starting'     ,
                        instance_id = instance_id    )

        except Exception as e:
            return dict(status='error', message=str(e))

    def get_audit_log(self) -> list:
        return [entry.json() for entry in self.audit_trail.get_entries()]
