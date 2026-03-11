from datetime  import datetime, timezone
from osbot_utils.type_safe.Type_Safe import Type_Safe


class EC2_Audit_Entry(Type_Safe):
    timestamp  : str  = ''
    action     : str  = ''
    admin      : str  = ''
    details    : dict
    prev_hash  : str  = ''
    entry_hash : str  = ''

    def __init__(self, **kwargs):
        if 'timestamp' not in kwargs or not kwargs['timestamp']:
            kwargs['timestamp'] = datetime.now(timezone.utc).isoformat()
        super().__init__(**kwargs)
