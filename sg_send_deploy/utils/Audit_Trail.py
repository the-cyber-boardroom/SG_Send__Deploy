from sg_send_deploy.ec2.schemas.EC2_Audit_Entry import EC2_Audit_Entry


class Audit_Trail:
    def __init__(self):
        self.entries   = []
        self.last_hash = ''

    def record(self, action: str, details: dict = None, admin: str = '') -> EC2_Audit_Entry:
        entry = EC2_Audit_Entry(
            action    = action          ,
            admin     = admin           ,
            details   = details or {}   ,
            prev_hash = self.last_hash  )
        entry.compute_hash()
        self.last_hash = entry.entry_hash
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
