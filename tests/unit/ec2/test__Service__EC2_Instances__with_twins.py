from unittest import TestCase

from sg_send_deploy.ec2.actions.Service__EC2_Budget      import Service__EC2_Budget
from sg_send_deploy.ec2.actions.Service__EC2_Instances    import Service__EC2_Instances
from sg_send_deploy.ec2.providers.EC2_Provider__Twin      import EC2_Provider__Twin
from sg_send_deploy.ec2.schemas.EC2_Budget_Config         import EC2_Budget_Config
from sg_send_deploy.twins.aws.ec2.Type__Twin__EC2__Fleet  import Type__Twin__EC2__Fleet
from sg_send_deploy.utils.Audit_Trail                     import Audit_Trail


class Test__Service__EC2_Instances__With_Twins(TestCase):

    def test_create__returns_created(self):
        fleet    = Type__Twin__EC2__Fleet()
        provider = EC2_Provider__Twin(fleet=fleet)
        service  = Service__EC2_Instances(ec2_provider=provider)

        result = service.create(
            instance_type = 't3.micro'       ,
            data_room_id  = 'room-001'       ,
            image_id      = 'ami-deploy-001' ,
            key_name      = 'sg-send-key'    ,
            admin         = 'test-admin'     )

        assert result['status']        == 'created'
        assert result['instance_id']   != ''
        assert result['instance_type'] == 't3.micro'
        assert result['data_room_id']  == 'room-001'

    def test_create__audit_logged(self):
        fleet    = Type__Twin__EC2__Fleet()
        provider = EC2_Provider__Twin(fleet=fleet)
        trail    = Audit_Trail()
        service  = Service__EC2_Instances(ec2_provider=provider, audit_trail=trail)

        service.create(
            instance_type = 't3.micro'   ,
            image_id      = 'ami-001'    ,
            admin         = 'admin-1'    )

        entries = trail.get_entries()
        assert len(entries) >= 1
        latest = entries[-1]
        assert latest.action == 'EC2_CREATE'
        assert latest.admin  == 'admin-1'

    def test_list_running__returns_running_instances(self):
        fleet    = Type__Twin__EC2__Fleet()
        provider = EC2_Provider__Twin(fleet=fleet)
        service  = Service__EC2_Instances(ec2_provider=provider)

        service.create(instance_type='t3.micro', image_id='ami-001')
        service.create(instance_type='t3.small', image_id='ami-001')

        running = service.list_running()
        assert len(running) == 2

    def test_budget__rejects_over_limit(self):
        fleet    = Type__Twin__EC2__Fleet()
        provider = EC2_Provider__Twin(fleet=fleet)
        config   = EC2_Budget_Config()
        config.max_instances  = 2
        config.enforce_limits = True
        budget   = Service__EC2_Budget(config=config)
        service  = Service__EC2_Instances(ec2_provider=provider, budget_service=budget)

        service.create(instance_type='t3.micro', image_id='ami-001')
        service.create(instance_type='t3.micro', image_id='ami-001')

        result = service.create(instance_type='t3.micro', image_id='ami-001')
        assert result['status']  == 'error'
        assert 'limit' in result['message'].lower()

    def test_audit_trail__chain_integrity(self):
        fleet    = Type__Twin__EC2__Fleet()
        provider = EC2_Provider__Twin(fleet=fleet)
        trail    = Audit_Trail()
        service  = Service__EC2_Instances(ec2_provider=provider, audit_trail=trail)

        service.create(instance_type='t3.micro', image_id='ami-001', admin='admin-a')
        service.create(instance_type='t3.micro', image_id='ami-001', admin='admin-b')

        assert trail.verify_chain() is True

    def test_get_instance__returns_details(self):
        fleet    = Type__Twin__EC2__Fleet()
        provider = EC2_Provider__Twin(fleet=fleet)
        service  = Service__EC2_Instances(ec2_provider=provider)

        result = service.create(instance_type='t3.micro', image_id='ami-001')
        instance_id = result['instance_id']

        details = service.get_instance(instance_id=instance_id)
        assert details['status']      == 'ok'
        assert details['instance_id'] == instance_id
        assert details['state']       == 'running'

    def test_terminate__works(self):
        fleet    = Type__Twin__EC2__Fleet()
        provider = EC2_Provider__Twin(fleet=fleet)
        trail    = Audit_Trail()
        service  = Service__EC2_Instances(ec2_provider=provider, audit_trail=trail)

        result = service.create(instance_type='t3.micro', image_id='ami-001')
        instance_id = result['instance_id']

        term_result = service.terminate(instance_id=instance_id, admin='admin-1')
        assert term_result['status']      == 'terminated'
        assert term_result['instance_id'] == instance_id

        entries = trail.get_entries()
        assert any(e.action == 'EC2_TERMINATE' for e in entries)
