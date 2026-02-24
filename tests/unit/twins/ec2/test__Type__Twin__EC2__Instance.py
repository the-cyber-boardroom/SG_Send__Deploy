from unittest import TestCase

from sg_send_deploy.twins.aws.ec2.Type__Twin__EC2__Instance import Type__Twin__EC2__Instance


class Test__Type__Twin__EC2__Instance(TestCase):

    def test_initial_state(self):
        twin = Type__Twin__EC2__Instance()
        assert twin.state.state_name == 'pending'
        assert twin.state.state_code == 0
        assert twin.config.instance_id == ''

    def test_run_instances(self):
        twin = Type__Twin__EC2__Instance()
        result = twin.execute('run_instances',
                              instance_type = 't3.micro'       ,
                              image_id      = 'ami-deploy-001' ,
                              key_name      = 'sg-send-key'    )

        assert twin.state.state_name       == 'running'
        assert twin.state.state_code       == 16
        assert twin.config.instance_id     != ''
        assert twin.config.instance_type   == 't3.micro'
        assert twin.config.image_id        == 'ami-deploy-001'
        assert twin.state.public_ip        != ''
        assert twin.state.private_ip       != ''
        assert twin.state.launch_time      != ''

        assert result['instance_id']       == twin.config.instance_id
        assert result['state']['Name']     == 'running'
        assert result['state']['Code']     == 16

    def test_stop_instances(self):
        twin = Type__Twin__EC2__Instance()
        twin.execute('run_instances', instance_type='t3.micro', image_id='ami-001')

        result = twin.execute('stop_instances')

        assert twin.state.state_name       == 'stopped'
        assert twin.state.public_ip        == ''
        assert result['previous_state']    == 'running'
        assert result['current_state']     == 'stopped'

    def test_start_stopped_instance(self):
        twin = Type__Twin__EC2__Instance()
        twin.execute('run_instances', instance_type='t3.micro', image_id='ami-001')
        twin.execute('stop_instances')

        result = twin.execute('start_instances')

        assert twin.state.state_name       == 'running'
        assert twin.state.public_ip        != ''
        assert result['previous_state']    == 'stopped'
        assert result['current_state']     == 'running'

    def test_terminate_instances(self):
        twin = Type__Twin__EC2__Instance()
        twin.execute('run_instances', instance_type='t3.micro', image_id='ami-001')

        result = twin.execute('terminate_instances')

        assert twin.state.state_name       == 'terminated'
        assert twin.state.state_code       == 48
        assert twin.state.public_ip        == ''
        assert twin.state.private_ip       == ''
        assert result['previous_state']    == 'running'
        assert result['current_state']     == 'terminated'

    def test_cannot_stop_stopped_instance(self):
        twin = Type__Twin__EC2__Instance()
        twin.execute('run_instances', instance_type='t3.micro', image_id='ami-001')
        twin.execute('stop_instances')

        result = twin.execute('stop_instances')
        assert result['status'] == 'error'

    def test_cannot_start_running_instance(self):
        twin = Type__Twin__EC2__Instance()
        twin.execute('run_instances', instance_type='t3.micro', image_id='ami-001')

        result = twin.execute('start_instances')
        assert result['status'] == 'error'

    def test_describe_instances__matches_aws_format(self):
        twin = Type__Twin__EC2__Instance()
        twin.execute('run_instances',
                     instance_type = 't3.micro'       ,
                     image_id      = 'ami-deploy-001' ,
                     key_name      = 'sg-send-key'    )

        result = twin.execute('describe_instances')

        expected_keys = {'instance_id', 'instance_type', 'image_id', 'key_name',
                         'state', 'public_ip', 'private_ip', 'launch_time',
                         'tags', 'region'}
        assert set(result.keys()) == expected_keys

    def test_unknown_action(self):
        twin = Type__Twin__EC2__Instance()
        result = twin.execute('nonexistent_action')
        assert result['status'] == 'error'
