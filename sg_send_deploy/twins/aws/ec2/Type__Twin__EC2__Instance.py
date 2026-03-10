from datetime import datetime, timezone

from sg_send_deploy.twins.aws.ec2.schemas.Schema__Twin__EC2__Instance import Schema__Twin__Config__EC2__Instance
from sg_send_deploy.twins.aws.ec2.schemas.Schema__Twin__EC2__Instance import Schema__Twin__State__EC2__Instance
from sg_send_deploy.twins.aws.Type__Twin__AWS                        import Type__Twin__AWS

EC2_STATE_CODES = dict(pending        = 0  ,
                       running        = 16 ,
                       shutting_down  = 32 ,
                       terminated     = 48 ,
                       stopping       = 64 ,
                       stopped        = 80 )

class Type__Twin__EC2__Instance(Type__Twin__AWS):
    config : Schema__Twin__Config__EC2__Instance
    state  : Schema__Twin__State__EC2__Instance

    def execute(self, action: str, **kwargs) -> dict:
        actions = dict(run_instances       = self.action__run_instances       ,
                       describe_instances  = self.action__describe_instances  ,
                       start_instances     = self.action__start_instances     ,
                       stop_instances      = self.action__stop_instances      ,
                       terminate_instances = self.action__terminate_instances )

        handler = actions.get(action)
        if handler is None:
            return dict(status='error', message=f'Unknown action: {action}')
        return handler(**kwargs)

    def action__run_instances(self, **kwargs) -> dict:
        instance_id   = kwargs.get('instance_id'  , self._generate_instance_id())
        instance_type = kwargs.get('instance_type', 't3.micro')
        image_id      = kwargs.get('image_id'     , ''         )
        key_name      = kwargs.get('key_name'     , ''         )

        self.config.instance_id   = instance_id
        self.config.instance_type = instance_type
        self.config.image_id      = image_id
        self.config.key_name      = key_name

        self.state.state_name  = 'pending'
        self.state.state_code  = EC2_STATE_CODES['pending']
        self.state.private_ip  = self._generate_private_ip()
        self.state.launch_time = datetime.now(timezone.utc).isoformat()

        self.state.state_name = 'running'
        self.state.state_code = EC2_STATE_CODES['running']
        self.state.public_ip  = self._generate_public_ip()

        return self.action__describe_instances()

    def action__describe_instances(self, **kwargs) -> dict:
        return dict(instance_id   = self.config.instance_id    ,
                    instance_type = self.config.instance_type   ,
                    image_id      = self.config.image_id        ,
                    key_name      = self.config.key_name        ,
                    state         = dict(Name = self.state.state_name ,
                                         Code = self.state.state_code),
                    public_ip     = self.state.public_ip        ,
                    private_ip    = self.state.private_ip       ,
                    launch_time   = self.state.launch_time      ,
                    tags          = self.config.tags             ,
                    region        = self.config.region           )

    def action__start_instances(self, **kwargs) -> dict:
        if self.state.state_name != 'stopped':
            return dict(status='error', message=f'Cannot start instance in state: {self.state.state_name}')

        prev_state = self.state.state_name
        self.state.state_name = 'pending'
        self.state.state_code = EC2_STATE_CODES['pending']

        self.state.state_name = 'running'
        self.state.state_code = EC2_STATE_CODES['running']
        self.state.public_ip  = self._generate_public_ip()

        return dict(instance_id    = self.config.instance_id  ,
                    previous_state = prev_state                ,
                    current_state  = self.state.state_name     )

    def action__stop_instances(self, **kwargs) -> dict:
        if self.state.state_name != 'running':
            return dict(status='error', message=f'Cannot stop instance in state: {self.state.state_name}')

        prev_state = self.state.state_name
        self.state.state_name = 'stopping'
        self.state.state_code = EC2_STATE_CODES['stopping']

        self.state.state_name = 'stopped'
        self.state.state_code = EC2_STATE_CODES['stopped']
        self.state.public_ip  = ''

        return dict(instance_id    = self.config.instance_id  ,
                    previous_state = prev_state                ,
                    current_state  = self.state.state_name     )

    def action__terminate_instances(self, **kwargs) -> dict:
        prev_state = self.state.state_name
        self.state.state_name = 'shutting-down'
        self.state.state_code = EC2_STATE_CODES['shutting_down']

        self.state.state_name = 'terminated'
        self.state.state_code = EC2_STATE_CODES['terminated']
        self.state.public_ip  = ''
        self.state.private_ip = ''

        return dict(instance_id    = self.config.instance_id  ,
                    previous_state = prev_state                ,
                    current_state  = self.state.state_name     )

    def _generate_instance_id(self) -> str:
        import hashlib
        seed = f'{self.config.image_id}-{self.config.instance_type}-{datetime.now(timezone.utc).isoformat()}'
        hash_val = hashlib.md5(seed.encode()).hexdigest()[:17]
        return f'i-{hash_val}'

    def _generate_private_ip(self) -> str:
        return '10.0.1.100'

    def _generate_public_ip(self) -> str:
        return '54.78.200.100'
