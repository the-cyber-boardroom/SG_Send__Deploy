from sg_send_deploy.twins.aws.Schema__Twin__AWS import Schema__Twin__Config__AWS
from sg_send_deploy.twins.aws.Schema__Twin__AWS import Schema__Twin__State__AWS

class Schema__Twin__Config__EC2__Security_Group(Schema__Twin__Config__AWS):
    group_id     : str = ''
    group_name   : str = ''
    description  : str = ''
    vpc_id       : str = ''

    def __init__(self, **kwargs):
        self.ingress_rules = kwargs.pop('ingress_rules', [])
        self.egress_rules  = kwargs.pop('egress_rules', [])
        super().__init__(**kwargs)


class Schema__Twin__State__EC2__Security_Group(Schema__Twin__State__AWS):

    def __init__(self, **kwargs):
        self.associated_instances = kwargs.pop('associated_instances', [])
        super().__init__(**kwargs)
