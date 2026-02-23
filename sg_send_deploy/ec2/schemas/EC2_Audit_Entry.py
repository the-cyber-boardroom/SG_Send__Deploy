import hashlib
import json
from datetime import datetime, timezone


class EC2_Audit_Entry:
    def __init__(self, action='', admin='', details=None, prev_hash='', timestamp='', entry_hash=''):
        self.timestamp  = timestamp or datetime.now(timezone.utc).isoformat()
        self.action     = action
        self.admin      = admin
        self.details    = details or {}
        self.prev_hash  = prev_hash
        self.entry_hash = entry_hash

    def compute_hash(self):
        data = json.dumps({
            'timestamp' : self.timestamp ,
            'action'    : self.action    ,
            'admin'     : self.admin     ,
            'details'   : self.details   ,
            'prev_hash' : self.prev_hash ,
        }, sort_keys=True)
        self.entry_hash = hashlib.sha256(data.encode()).hexdigest()
        return self.entry_hash

    def json(self):
        return dict(
            timestamp  = self.timestamp  ,
            action     = self.action     ,
            admin      = self.admin      ,
            details    = self.details    ,
            prev_hash  = self.prev_hash  ,
            entry_hash = self.entry_hash )
