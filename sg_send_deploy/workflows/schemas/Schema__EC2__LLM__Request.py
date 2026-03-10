from osbot_utils.type_safe.Type_Safe import Type_Safe


class Schema__EC2__LLM__Request(Type_Safe):
    ami_id          : str  = ''
    instance_type   : str  = 'c7g.xlarge'
    spot_instance   : bool = True
    runner_ip       : str  = ''
    model           : str  = 'gemma3:4b'
    checks          : list
