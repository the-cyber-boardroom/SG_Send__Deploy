from sg_send_deploy.twins.aws.Schema__Twin__AWS import Schema__Twin__Config__AWS
from sg_send_deploy.twins.aws.Schema__Twin__AWS import Schema__Twin__State__AWS

class Schema__Twin__Config__EC2__Instance(Schema__Twin__Config__AWS):
    instance_id    : str = ''
    instance_type  : str = 't3.micro'
    image_id       : str = ''
    key_name       : str = ''
    subnet_id      : str = ''
    vpc_id         : str = ''

    def __init__(self, **kwargs):
        self.security_groups = kwargs.pop('security_groups', [])
        self.tags            = kwargs.pop('tags', {})
        super().__init__(**kwargs)


class Schema__Twin__State__EC2__Instance(Schema__Twin__State__AWS):
    state_name     : str = 'pending'
    state_code     : int = 0
    public_ip      : str = ''
    private_ip     : str = ''
    launch_time    : str = ''
    uptime_seconds : int = 0
