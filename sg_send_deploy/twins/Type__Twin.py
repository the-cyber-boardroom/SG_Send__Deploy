from osbot_utils.type_safe.Type_Safe import Type_Safe
from sg_send_deploy.twins.Schema__Twin import Schema__Twin__Config
from sg_send_deploy.twins.Schema__Twin import Schema__Twin__State

class Type__Twin(Type_Safe):
    config : Schema__Twin__Config
    state  : Schema__Twin__State

    def execute(self, action: str, **kwargs) -> dict:
        raise NotImplementedError()
