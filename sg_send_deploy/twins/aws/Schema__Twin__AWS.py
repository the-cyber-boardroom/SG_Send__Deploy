from sg_send_deploy.twins.Schema__Twin import Schema__Twin__Config
from sg_send_deploy.twins.Schema__Twin import Schema__Twin__State

class Schema__Twin__Config__AWS(Schema__Twin__Config):
    region     : str = 'eu-west-2'
    account_id : str = ''

class Schema__Twin__State__AWS(Schema__Twin__State):
    pass
