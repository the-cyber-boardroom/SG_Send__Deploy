from unittest import TestCase

from sg_send_deploy.utils.Audit_Trail import Audit_Trail


class Test__Audit_Trail(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.audit_trail = Audit_Trail()

    def test_record__creates_entry(self):
        entry = self.audit_trail.record(
            action  = 'EC2_CREATE'                      ,
            admin   = 'test-admin'                      ,
            details = dict(instance_id = 'i-test123'    ))

        assert entry.action     == 'EC2_CREATE'
        assert entry.admin      == 'test-admin'
        assert entry.entry_hash != ''
        assert entry.details['instance_id'] == 'i-test123'

    def test_record__chain_integrity(self):
        trail = Audit_Trail()
        entry_1 = trail.record(action='ACTION_1', admin='admin-1')
        entry_2 = trail.record(action='ACTION_2', admin='admin-2')

        assert entry_2.prev_hash == entry_1.entry_hash
        assert trail.verify_chain() is True

    def test_get_entries__returns_all(self):
        trail = Audit_Trail()
        trail.record(action='A')
        trail.record(action='B')
        trail.record(action='C')

        entries = trail.get_entries()
        assert len(entries) == 3
        assert entries[0].action == 'A'
        assert entries[2].action == 'C'

    def test_verify_chain__empty_is_valid(self):
        trail = Audit_Trail()
        assert trail.verify_chain() is True
