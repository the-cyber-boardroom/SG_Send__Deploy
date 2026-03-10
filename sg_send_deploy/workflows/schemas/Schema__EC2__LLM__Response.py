from osbot_utils.type_safe.Type_Safe import Type_Safe


class Schema__EC2__LLM__Response(Type_Safe):
    success           : bool  = False
    instance_id       : str   = ''
    instance_type     : str   = ''
    spot_fulfilled    : bool  = False
    boot_time_seconds : float = 0.0
    results           : list
    total_duration_ms : int   = 0
    error             : str   = ''
