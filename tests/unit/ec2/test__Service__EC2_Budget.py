from unittest import TestCase

from sg_send_deploy.ec2.actions.Service__EC2_Budget import Service__EC2_Budget
from sg_send_deploy.ec2.schemas.EC2_Budget_Config   import EC2_Budget_Config


class Test__Service__EC2_Budget(TestCase):

    @classmethod
    def setUpClass(cls):
        config = EC2_Budget_Config()
        config.max_instances = 3
        cls.budget_service = Service__EC2_Budget(config=config)

    def test_check_instance_limit__under_limit(self):
        result = self.budget_service.check_instance_limit(current_count=2)
        assert result['allowed']  is True
        assert result['message']  == ''

    def test_check_instance_limit__at_limit(self):
        result = self.budget_service.check_instance_limit(current_count=3)
        assert result['allowed']  is False
        assert 'limit reached' in result['message']

    def test_check_instance_limit__over_limit(self):
        result = self.budget_service.check_instance_limit(current_count=5)
        assert result['allowed']  is False

    def test_check_instance_type__allowed(self):
        result = self.budget_service.check_instance_type(instance_type='t3.micro')
        assert result['allowed'] is True

    def test_check_instance_type__not_allowed(self):
        result = self.budget_service.check_instance_type(instance_type='m5.xlarge')
        assert result['allowed'] is False
        assert 'not allowed' in result['message']

    def test_check_can_create__all_ok(self):
        result = self.budget_service.check_can_create(current_count=1, instance_type='t3.micro')
        assert result['allowed'] is True

    def test_check_can_create__limit_reached(self):
        result = self.budget_service.check_can_create(current_count=3, instance_type='t3.micro')
        assert result['allowed'] is False

    def test_check_can_create__bad_type(self):
        result = self.budget_service.check_can_create(current_count=0, instance_type='p3.2xlarge')
        assert result['allowed'] is False
