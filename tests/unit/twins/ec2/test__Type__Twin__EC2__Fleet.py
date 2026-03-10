from unittest import TestCase

from sg_send_deploy.twins.aws.ec2.Type__Twin__EC2__Fleet import Type__Twin__EC2__Fleet


class Test__Type__Twin__EC2__Fleet(TestCase):

    def test_create_and_list(self):
        fleet = Type__Twin__EC2__Fleet()
        fleet.create_instance(instance_type='t3.micro', image_id='ami-001')
        fleet.create_instance(instance_type='t3.small', image_id='ami-002')

        instances = fleet.list_instances()
        assert len(instances) == 2

    def test_running_count(self):
        fleet = Type__Twin__EC2__Fleet()
        fleet.create_instance(instance_type='t3.micro', image_id='ami-001')
        fleet.create_instance(instance_type='t3.micro', image_id='ami-002')

        assert fleet.running_count() == 2

    def test_terminate_reduces_running(self):
        fleet = Type__Twin__EC2__Fleet()
        r1 = fleet.create_instance(instance_type='t3.micro', image_id='ami-001')

        instance_id = r1['instance_id']
        fleet.terminate_instance(instance_id=instance_id)

        running = fleet.list_instances(state_filter='running')
        assert len(running) == 0

    def test_stop_and_start(self):
        fleet = Type__Twin__EC2__Fleet()
        r1 = fleet.create_instance(instance_type='t3.micro', image_id='ami-001')
        instance_id = r1['instance_id']

        fleet.stop_instance(instance_id=instance_id)
        assert fleet.running_count() == 0

        fleet.start_instance(instance_id=instance_id)
        assert fleet.running_count() == 1

    def test_describe_nonexistent(self):
        fleet = Type__Twin__EC2__Fleet()
        result = fleet.describe_instance(instance_id='i-nonexistent')
        assert result['status'] == 'error'
