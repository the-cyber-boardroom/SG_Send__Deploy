from sg_send_deploy.twins.aws.Schema__Twin__AWS import Schema__Twin__Config__AWS
from sg_send_deploy.twins.aws.Schema__Twin__AWS import Schema__Twin__State__AWS

class Schema__Twin__Config__EC2__Security_Group(Schema__Twin__Config__AWS):
    group_id      : str  = ''
    group_name    : str  = ''
    description   : str  = ''
    vpc_id        : str  = ''
    ingress_rules : list
    egress_rules  : list


class Schema__Twin__State__EC2__Security_Group(Schema__Twin__State__AWS):
    associated_instances : list
