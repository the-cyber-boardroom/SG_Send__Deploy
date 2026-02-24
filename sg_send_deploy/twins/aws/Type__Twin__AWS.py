from sg_send_deploy.twins.Type__Twin                import Type__Twin
from sg_send_deploy.twins.aws.Schema__Twin__AWS     import Schema__Twin__Config__AWS
from sg_send_deploy.twins.aws.Schema__Twin__AWS     import Schema__Twin__State__AWS

class Type__Twin__AWS(Type__Twin):
    config : Schema__Twin__Config__AWS
    state  : Schema__Twin__State__AWS
