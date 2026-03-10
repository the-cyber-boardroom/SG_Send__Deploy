from osbot_utils.type_safe.Type_Safe import Type_Safe


class Schema__QA__Result(Type_Safe):
    check_id        : str   = ''
    passed          : bool  = False
    findings        : list
    raw_response    : str   = ''
    tokens_per_sec  : float = 0.0
    duration_ms     : int   = 0
