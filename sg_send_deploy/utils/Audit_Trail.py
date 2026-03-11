from osbot_utils.helpers.cache.Cache__Hash__Generator import Cache__Hash__Generator
from osbot_utils.type_safe.Type_Safe                 import Type_Safe
from sg_send_deploy.ec2.schemas.EC2_Audit_Entry      import EC2_Audit_Entry


class Audit_Trail(Type_Safe):
    entries        : list
    last_hash      : str = ''
    hash_generator : Cache__Hash__Generator

    def record(self, action: str, details: dict = None, admin: str = '') -> EC2_Audit_Entry:
        entry = EC2_Audit_Entry(
            action    = action          ,
            admin     = admin           ,
            details   = details or {}   ,
            prev_hash = self.last_hash  )
        entry.entry_hash = self.hash_generator.from_type_safe(entry, exclude_fields=['entry_hash'])
        self.last_hash   = entry.entry_hash
        self.entries.append(entry)
        return entry

    def get_entries(self) -> list:
        return self.entries

    def verify_chain(self) -> bool:
        prev_hash = ''
        for entry in self.entries:
            if entry.prev_hash != prev_hash:
                return False
            prev_hash = entry.entry_hash
        return True
