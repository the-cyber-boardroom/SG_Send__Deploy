from datetime import datetime, timezone, timedelta
from unittest import TestCase

from sg_send_deploy.ec2.providers.EC2_Provider__Twin      import EC2_Provider__Twin
from sg_send_deploy.lambda__watchdog.Watchdog__Service    import Watchdog__Service
from sg_send_deploy.twins.aws.ec2.Type__Twin__EC2__Fleet  import Type__Twin__EC2__Fleet


def create_test_watchdog(idle_timeout_minutes=30):
    fleet    = Type__Twin__EC2__Fleet()
    provider = EC2_Provider__Twin(fleet=fleet)
    watchdog = Watchdog__Service(ec2_provider         = provider              ,
                                 idle_timeout_minutes = idle_timeout_minutes  )
    return watchdog, fleet


class Test__Watchdog__Service(TestCase):

    def test_check_and_stop_idle__no_instances(self):
        watchdog, _ = create_test_watchdog()

        result = watchdog.check_and_stop_idle()

        assert result['checked'] == 0
        assert result['actions'] == []

    def test_check_and_stop_idle__no_managed_instances(self):
        watchdog, fleet = create_test_watchdog()

        fleet.create_instance(image_id='ami-001', instance_type='t3.micro')

        result = watchdog.check_and_stop_idle()

        assert result['checked'] == 0
        assert result['actions'] == []

    def test_check_and_stop_idle__managed_but_healthy_skip(self):
        watchdog, fleet = create_test_watchdog(idle_timeout_minutes=9999)

        instance = fleet.create_instance(
            image_id      = 'ami-001'      ,
            instance_type = 't3.micro'     ,
            tags          = {'sg-deploy:managed': 'true'})

        result = watchdog.check_and_stop_idle()

        assert result['checked'] == 1
        running = fleet.list_instances(state_filter='running')
        assert len(running) == 1

    def test_check_and_stop_idle__unhealthy_and_past_timeout(self):
        watchdog, fleet = create_test_watchdog(idle_timeout_minutes=0)

        instance = fleet.create_instance(
            image_id      = 'ami-001'      ,
            instance_type = 't3.micro'     ,
            tags          = {'sg-deploy:managed': 'true'})

        instance_id = instance['instance_id']

        twin = fleet.instances[instance_id]
        past = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        twin.state.launch_time = past

        result = watchdog.check_and_stop_idle()

        assert result['checked'] == 1
        assert len(result['actions']) == 1
        assert result['actions'][0]['action'] == 'stopped'
        assert result['actions'][0]['instance_id'] == instance_id

    def test_check_and_stop_idle__stopped_instance_ignored(self):
        watchdog, fleet = create_test_watchdog(idle_timeout_minutes=0)

        instance = fleet.create_instance(
            image_id      = 'ami-001'      ,
            instance_type = 't3.micro'     ,
            tags          = {'sg-deploy:managed': 'true'})

        fleet.stop_instance(instance['instance_id'])

        result = watchdog.check_and_stop_idle()

        assert result['actions'] == []

    def test_exceeds_idle_timeout__true(self):
        watchdog, _ = create_test_watchdog(idle_timeout_minutes=30)
        past = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        assert watchdog._exceeds_idle_timeout(past) is True

    def test_exceeds_idle_timeout__false(self):
        watchdog, _ = create_test_watchdog(idle_timeout_minutes=30)
        recent = datetime.now(timezone.utc).isoformat()
        assert watchdog._exceeds_idle_timeout(recent) is False
