from unittest import TestCase

from sg_send_deploy.ec2.schemas.EC2__Types         import EC2__Instance_Id
from sg_send_deploy.ec2.schemas.EC2__Types         import EC2__AMI_Id
from sg_send_deploy.ec2.schemas.EC2__Types         import EC2__Security_Group_Id
from sg_send_deploy.ec2.schemas.EC2__Types         import EC2__Key_Name
from sg_send_deploy.ec2.schemas.EC2__Types         import EC2__VPC_Id
from sg_send_deploy.ec2.schemas.EC2__Types         import EC2__Subnet_Id
from sg_send_deploy.ec2.schemas.EC2__Types         import Enum__EC2__Instance_Type
from sg_send_deploy.ec2.schemas.EC2__Types         import Enum__EC2__Instance_State
from sg_send_deploy.schemas.Deploy__Types          import Admin_Id
from sg_send_deploy.schemas.Deploy__Types          import Audit__Action_Id
from sg_send_deploy.workflows.schemas.QA__Types    import QA__Check_Id


class Test__EC2__Named_Ids(TestCase):

    def test_instance_id__accepts_aws_format(self):
        id_val = EC2__Instance_Id('i-0abc123def456')
        assert str(id_val) == 'i-0abc123def456'

    def test_ami_id__accepts_aws_format(self):
        id_val = EC2__AMI_Id('ami-deploy-001')
        assert str(id_val) == 'ami-deploy-001'

    def test_security_group_id(self):
        id_val = EC2__Security_Group_Id('sg-abc123')
        assert str(id_val) == 'sg-abc123'

    def test_key_name(self):
        id_val = EC2__Key_Name('sg-send-key')
        assert str(id_val) == 'sg-send-key'

    def test_vpc_id(self):
        id_val = EC2__VPC_Id('vpc-abc123')
        assert str(id_val) == 'vpc-abc123'

    def test_subnet_id(self):
        id_val = EC2__Subnet_Id('subnet-abc123')
        assert str(id_val) == 'subnet-abc123'


class Test__Deploy__Named_Ids(TestCase):

    def test_admin_id(self):
        id_val = Admin_Id('test-admin')
        assert str(id_val) == 'test-admin'

    def test_audit_action_id(self):
        id_val = Audit__Action_Id('EC2_CREATE')
        assert str(id_val) == 'EC2_CREATE'

    def test_qa_check_id(self):
        id_val = QA__Check_Id('check-001')
        assert str(id_val) == 'check-001'


class Test__EC2__Enums(TestCase):

    def test_instance_type__string_conversion(self):
        assert str(Enum__EC2__Instance_Type.T3_MICRO)  == 't3.micro'
        assert str(Enum__EC2__Instance_Type.T3_SMALL)  == 't3.small'
        assert str(Enum__EC2__Instance_Type.T3_MEDIUM) == 't3.medium'

    def test_instance_type__from_string(self):
        assert Enum__EC2__Instance_Type('t3.micro') == Enum__EC2__Instance_Type.T3_MICRO

    def test_instance_state__all_six_states(self):
        assert str(Enum__EC2__Instance_State.PENDING)       == 'pending'
        assert str(Enum__EC2__Instance_State.RUNNING)       == 'running'
        assert str(Enum__EC2__Instance_State.SHUTTING_DOWN) == 'shutting-down'
        assert str(Enum__EC2__Instance_State.TERMINATED)    == 'terminated'
        assert str(Enum__EC2__Instance_State.STOPPING)      == 'stopping'
        assert str(Enum__EC2__Instance_State.STOPPED)       == 'stopped'

    def test_instance_state__from_string(self):
        assert Enum__EC2__Instance_State('running') == Enum__EC2__Instance_State.RUNNING
