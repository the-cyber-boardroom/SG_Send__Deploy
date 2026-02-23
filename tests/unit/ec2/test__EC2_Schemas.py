from unittest import TestCase

from sg_send_deploy.ec2.schemas.EC2_Instance_Info  import EC2_Instance_Info
from sg_send_deploy.ec2.schemas.EC2_Budget_Config  import EC2_Budget_Config
from sg_send_deploy.ec2.schemas.EC2_Audit_Entry    import EC2_Audit_Entry


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

    def test_compute_hash(self):
        entry = EC2_Audit_Entry(action='TEST', admin='test-admin')
        hash_value = entry.compute_hash()
        assert hash_value != ''
        assert entry.entry_hash == hash_value
        assert len(hash_value)  == 64

    def test_compute_hash__deterministic(self):
        entry = EC2_Audit_Entry(action='TEST', admin='admin', timestamp='2026-02-23T00:00:00')
        hash_1 = entry.compute_hash()
        hash_2 = entry.compute_hash()
        assert hash_1 == hash_2
