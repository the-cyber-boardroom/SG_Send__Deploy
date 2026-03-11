from unittest import TestCase

from sg_send_deploy.ec2.schemas.EC2_Instance_Info  import EC2_Instance_Info
from sg_send_deploy.ec2.schemas.EC2_Budget_Config  import EC2_Budget_Config
from sg_send_deploy.ec2.schemas.EC2_Audit_Entry    import EC2_Audit_Entry
from sg_send_deploy.utils.Audit_Trail              import Audit_Trail


class Test__EC2_Instance_Info(TestCase):

    def test_default_values(self):
        info = EC2_Instance_Info()
        assert info.instance_id   == ''
        assert info.status        == ''
        assert info.public_ip     == ''
        assert info.instance_type == ''
        assert info.uptime_seconds == 0

    def test_set_values(self):
        info = EC2_Instance_Info(
            instance_id   = 'i-abc123'  ,
            status        = 'running'   ,
            public_ip     = '1.2.3.4'   ,
            instance_type = 't3.micro'  )
        assert info.instance_id   == 'i-abc123'
        assert info.status        == 'running'
        assert info.public_ip     == '1.2.3.4'
        assert info.instance_type == 't3.micro'


class Test__EC2_Budget_Config(TestCase):

    def test_default_values(self):
        config = EC2_Budget_Config()
        assert config.max_instances     == 5
        assert config.daily_budget_usd  == 10.0
        assert config.idle_timeout_minutes == 30
        assert 't3.micro' in config.allowed_types()


class Test__EC2_Audit_Entry(TestCase):

    def test_default_values(self):
        entry = EC2_Audit_Entry()
        assert entry.action     == ''
        assert entry.timestamp  != ''
        assert entry.entry_hash == ''

    def test_hash_via_audit_trail(self):
        trail = Audit_Trail()
        entry = trail.record(action='TEST', admin='test-admin')
        assert entry.entry_hash != ''

    def test_hash_via_audit_trail__deterministic(self):
        trail_1 = Audit_Trail()
        trail_2 = Audit_Trail()
        entry_1 = trail_1.record(action='TEST', admin='admin')
        entry_2 = trail_2.record(action='TEST', admin='admin')
        assert entry_1.entry_hash != ''
        assert entry_2.entry_hash != ''

    def test_type_safe_json(self):
        entry = EC2_Audit_Entry(action='TEST', admin='test-admin')
        data  = entry.json()
        assert data['action'] == 'TEST'
        assert data['admin']  == 'test-admin'
        assert 'timestamp'    in data
        assert 'entry_hash'   in data
