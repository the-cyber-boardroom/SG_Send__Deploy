from unittest import TestCase

from fastapi                                             import FastAPI
from fastapi.testclient                                  import TestClient
from sg_send_deploy.ec2.actions.Service__EC2_Budget      import Service__EC2_Budget
from sg_send_deploy.ec2.actions.Service__EC2_Instances    import Service__EC2_Instances
from sg_send_deploy.ec2.providers.EC2_Provider__Twin      import EC2_Provider__Twin
from sg_send_deploy.ec2.routes.Routes__EC2_Instances      import Routes__EC2_Instances
from sg_send_deploy.ec2.schemas.EC2_Budget_Config         import EC2_Budget_Config
from sg_send_deploy.twins.aws.ec2.Type__Twin__EC2__Fleet  import Type__Twin__EC2__Fleet
from sg_send_deploy.utils.Audit_Trail                     import Audit_Trail


def create_test_app(max_instances=5):
    fleet    = Type__Twin__EC2__Fleet()
    provider = EC2_Provider__Twin(fleet=fleet)
    config   = EC2_Budget_Config()
    config.max_instances = max_instances
    budget   = Service__EC2_Budget(config=config)
    trail    = Audit_Trail()
    service  = Service__EC2_Instances(ec2_provider   = provider ,
                                      budget_service = budget   ,
                                      audit_trail    = trail    )

    app    = FastAPI()
    routes = Routes__EC2_Instances(app=app, service_instances=service)
    routes.setup()

    return TestClient(app), service, trail


class Test__Routes__EC2_Instances__With_Twins(TestCase):

    def test_get_instances__empty(self):
        client, _, _ = create_test_app()

        response = client.get('/ec2/instances')

        assert response.status_code == 200
        assert response.json() == []

    def test_post_create_instance__returns_created(self):
        client, _, _ = create_test_app()

        response = client.post('/ec2/create-instance', params={
            'instance_type': 't3.micro'       ,
            'image_id'     : 'ami-deploy-001' ,
            'data_room_id' : 'room-demo'      ,
            'key_name'     : 'sg-send-key'    })

        assert response.status_code == 200
        data = response.json()
        assert data['status']        == 'created'
        assert data['instance_id']   != ''
        assert data['instance_type'] == 't3.micro'
        assert data['data_room_id']  == 'room-demo'

    def test_get_instances__after_create(self):
        client, _, _ = create_test_app()

        client.post('/ec2/create-instance', params={
            'instance_type': 't3.micro'  ,
            'image_id'     : 'ami-001'   })

        response = client.get('/ec2/instances')
        assert response.status_code == 200
        instances = response.json()
        assert len(instances) == 1
        assert instances[0]['status'] == 'running'

    def test_get_instance__by_id(self):
        client, _, _ = create_test_app()

        create_resp = client.post('/ec2/create-instance', params={
            'instance_type': 't3.micro' ,
            'image_id'     : 'ami-001'  })
        instance_id = create_resp.json()['instance_id']

        response = client.get(f'/ec2/instances/{instance_id}')
        assert response.status_code == 200
        data = response.json()
        assert data['status']      == 'ok'
        assert data['instance_id'] == instance_id
        assert data['state']       == 'running'

    def test_delete_terminate__removes_from_running(self):
        client, _, _ = create_test_app()

        create_resp = client.post('/ec2/create-instance', params={
            'instance_type': 't3.micro' ,
            'image_id'     : 'ami-001'  })
        instance_id = create_resp.json()['instance_id']

        term_resp = client.delete(f'/ec2/terminate/{instance_id}')
        assert term_resp.status_code == 200
        assert term_resp.json()['status'] == 'terminated'

        running = client.get('/ec2/instances').json()
        assert len(running) == 0

    def test_post_stop__then_start(self):
        client, _, _ = create_test_app()

        create_resp = client.post('/ec2/create-instance', params={
            'instance_type': 't3.micro' ,
            'image_id'     : 'ami-001'  })
        instance_id = create_resp.json()['instance_id']

        stop_resp = client.post(f'/ec2/stop/{instance_id}')
        assert stop_resp.status_code == 200
        assert stop_resp.json()['status'] == 'stopping'

        running = client.get('/ec2/instances').json()
        assert len(running) == 0

        start_resp = client.post(f'/ec2/start/{instance_id}')
        assert start_resp.status_code == 200
        assert start_resp.json()['status'] == 'starting'

        running = client.get('/ec2/instances').json()
        assert len(running) == 1

    def test_get_audit_log__records_operations(self):
        client, _, _ = create_test_app()

        client.post('/ec2/create-instance', params={
            'instance_type': 't3.micro' ,
            'image_id'     : 'ami-001'  })

        response = client.get('/ec2/audit-log')
        assert response.status_code == 200
        entries = response.json()
        assert len(entries) >= 1
        assert entries[0]['action'] == 'EC2_CREATE'

    def test_budget_limit__enforced_via_api(self):
        client, _, _ = create_test_app(max_instances=2)

        client.post('/ec2/create-instance', params={
            'instance_type': 't3.micro', 'image_id': 'ami-001'})
        client.post('/ec2/create-instance', params={
            'instance_type': 't3.micro', 'image_id': 'ami-001'})

        resp = client.post('/ec2/create-instance', params={
            'instance_type': 't3.micro', 'image_id': 'ami-001'})

        assert resp.status_code == 200
        data = resp.json()
        assert data['status'] == 'error'
        assert 'limit' in data['message'].lower()

    def test_instance_type__rejected_via_api(self):
        client, _, _ = create_test_app()

        resp = client.post('/ec2/create-instance', params={
            'instance_type': 'p3.2xlarge' ,
            'image_id'     : 'ami-001'    })

        data = resp.json()
        assert data['status'] == 'error'
        assert 'not allowed' in data['message'].lower()

    def test_full_lifecycle__create_stop_start_terminate(self):
        client, _, trail = create_test_app()

        r = client.post('/ec2/create-instance', params={
            'instance_type': 't3.micro' ,
            'image_id'     : 'ami-001'  })
        instance_id = r.json()['instance_id']

        client.post(f'/ec2/stop/{instance_id}')
        client.post(f'/ec2/start/{instance_id}')
        client.delete(f'/ec2/terminate/{instance_id}')

        assert trail.verify_chain() is True

        entries = trail.get_entries()
        actions = [e.action for e in entries]
        assert 'EC2_CREATE'    in actions
        assert 'EC2_STOP'      in actions
        assert 'EC2_START'     in actions
        assert 'EC2_TERMINATE' in actions
