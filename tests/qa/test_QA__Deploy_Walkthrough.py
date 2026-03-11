"""QA walkthrough: step-by-step deploy service operations.

Two test classes:
    1. Test_QA__Deploy_Walkthrough__Local  — uses twins (no AWS keys needed)
    2. Test_QA__Deploy_Walkthrough__AWS    — uses real AWS (needs credentials)

Run individual tests in order with -s to see output:

    # Local walkthrough (no AWS keys needed):
    pytest tests/qa/test_QA__Deploy_Walkthrough.py::Test_QA__Deploy_Walkthrough__Local::test__01__create_twin_fleet -s
    pytest tests/qa/test_QA__Deploy_Walkthrough.py::Test_QA__Deploy_Walkthrough__Local::test__02__create_instance -s
    pytest tests/qa/test_QA__Deploy_Walkthrough.py::Test_QA__Deploy_Walkthrough__Local::test__03__list_running -s
    pytest tests/qa/test_QA__Deploy_Walkthrough.py::Test_QA__Deploy_Walkthrough__Local::test__04__check_status_endpoint -s
    pytest tests/qa/test_QA__Deploy_Walkthrough.py::Test_QA__Deploy_Walkthrough__Local::test__05__budget_check -s
    pytest tests/qa/test_QA__Deploy_Walkthrough.py::Test_QA__Deploy_Walkthrough__Local::test__06__stop_and_start -s
    pytest tests/qa/test_QA__Deploy_Walkthrough.py::Test_QA__Deploy_Walkthrough__Local::test__07__watchdog_skips_healthy -s
    pytest tests/qa/test_QA__Deploy_Walkthrough.py::Test_QA__Deploy_Walkthrough__Local::test__08__watchdog_stops_idle -s
    pytest tests/qa/test_QA__Deploy_Walkthrough.py::Test_QA__Deploy_Walkthrough__Local::test__09__terminate_and_audit -s
    pytest tests/qa/test_QA__Deploy_Walkthrough.py::Test_QA__Deploy_Walkthrough__Local::test__10__full_audit_chain -s

    # AWS walkthrough (needs AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION):
    pytest tests/qa/test_QA__Deploy_Walkthrough.py::Test_QA__Deploy_Walkthrough__AWS::test__1__verify_credentials -s
    pytest tests/qa/test_QA__Deploy_Walkthrough.py::Test_QA__Deploy_Walkthrough__AWS::test__2__list_existing_instances -s
    pytest tests/qa/test_QA__Deploy_Walkthrough.py::Test_QA__Deploy_Walkthrough__AWS::test__3__create_instance -s
    pytest tests/qa/test_QA__Deploy_Walkthrough.py::Test_QA__Deploy_Walkthrough__AWS::test__4__check_status -s
    pytest tests/qa/test_QA__Deploy_Walkthrough.py::Test_QA__Deploy_Walkthrough__AWS::test__5__terminate_instance -s

Notes:
    - Local tests share state via module-level variables (run in order).
    - AWS tests create REAL EC2 instances (costs money, cleans up on terminate).
    - The -s flag shows all print output so you can see what's happening.
"""

import json
import os
from datetime    import datetime, timezone, timedelta
from unittest    import TestCase

import pytest

from sg_send_deploy.ec2.actions.Service__EC2_Budget      import Service__EC2_Budget
from sg_send_deploy.ec2.actions.Service__EC2_Instances    import Service__EC2_Instances
from sg_send_deploy.ec2.providers.EC2_Provider__Twin      import EC2_Provider__Twin
from sg_send_deploy.ec2.schemas.EC2_Budget_Config         import EC2_Budget_Config
from sg_send_deploy.lambda__watchdog.Watchdog__Service    import Watchdog__Service
from sg_send_deploy.server.routes.Routes__Status          import Routes__Status
from sg_send_deploy.twins.aws.ec2.Type__Twin__EC2__Fleet  import Type__Twin__EC2__Fleet
from sg_send_deploy.utils.Audit_Trail                     import Audit_Trail


# ---------------------------------------------------------------------------
# Shared state for local walkthrough (persists across tests when run in order)
# ---------------------------------------------------------------------------
_local = dict(
    fleet    = None,
    provider = None,
    service  = None,
    trail    = None,
    budget   = None,
    watchdog = None,
    instance_id = '',
)


def _print_section(title):
    print(f'\n{"=" * 60}')
    print(f'  {title}')
    print(f'{"=" * 60}')


def _print_json(label, data):
    print(f'\n  {label}:')
    print(f'    {json.dumps(data, indent=2, default=str)}')


# ===========================================================================
# Part 1: LOCAL walkthrough (no AWS keys needed — uses twins)
# ===========================================================================
class Test_QA__Deploy_Walkthrough__Local(TestCase):

    # -----------------------------------------------------------------------
    # Step 1: Set up the twin fleet
    # -----------------------------------------------------------------------
    def test__01__create_twin_fleet(self):
        _print_section('Step 1: Create twin fleet and services')

        _local['fleet']    = Type__Twin__EC2__Fleet()
        _local['provider'] = EC2_Provider__Twin(fleet=_local['fleet'])
        _local['trail']    = Audit_Trail()

        config = EC2_Budget_Config()
        config.max_instances  = 3
        config.enforce_limits = True
        _local['budget'] = Service__EC2_Budget(config=config)

        _local['service'] = Service__EC2_Instances(
            ec2_provider   = _local['provider'] ,
            budget_service = _local['budget']   ,
            audit_trail    = _local['trail']    )

        print(f'  Fleet created:     {_local["fleet"]}')
        print(f'  Provider:          EC2_Provider__Twin (in-memory)')
        print(f'  Budget:            max {config.max_instances} instances, enforce={config.enforce_limits}')
        print(f'  Audit trail:       hash-chained, entries={len(_local["trail"].entries)}')
        print(f'\n  Everything is in-memory. No AWS calls.')

    # -----------------------------------------------------------------------
    # Step 2: Create an EC2 instance
    # -----------------------------------------------------------------------
    def test__02__create_instance(self):
        _print_section('Step 2: Create an EC2 instance')

        service = _local['service']
        result  = service.create(
            instance_type = 't3.micro'       ,
            data_room_id  = 'demo-room-001'  ,
            image_id      = 'ami-deploy-001' ,
            key_name      = 'sg-send-key'    ,
            admin         = 'qa-tester'      )

        _local['instance_id'] = result.get('instance_id', '')

        _print_json('Create result', result)

        assert result['status'] == 'created', f'Expected created, got: {result}'
        print(f'\n  Instance ID: {_local["instance_id"]}')
        print(f'  Data room:   demo-room-001')

    # -----------------------------------------------------------------------
    # Step 3: List running instances
    # -----------------------------------------------------------------------
    def test__03__list_running(self):
        _print_section('Step 3: List running instances')

        service  = _local['service']
        running  = service.list_running()

        print(f'  Running instances: {len(running)}')
        for i, inst in enumerate(running):
            print(f'\n  Instance {i + 1}:')
            print(f'    ID:         {inst["instance_id"]}')
            print(f'    Status:     {inst["status"]}')
            print(f'    Type:       {inst["instance_type"]}')
            print(f'    Public IP:  {inst["public_ip"]}')
            print(f'    Private IP: {inst["private_ip"]}')
            print(f'    AMI:        {inst["ami_id"]}')

        assert len(running) == 1

    # -----------------------------------------------------------------------
    # Step 4: Test the status endpoint
    # -----------------------------------------------------------------------
    def test__04__check_status_endpoint(self):
        _print_section('Step 4: Test /deploy/status endpoint')

        from fastapi            import FastAPI
        from fastapi.testclient import TestClient

        app    = FastAPI()
        routes = Routes__Status(app=app, ec2_provider=_local['provider'])
        routes.setup()
        client = TestClient(app)

        # Without DEPLOY_INSTANCE_ID
        os.environ.pop('DEPLOY_INSTANCE_ID', None)
        resp = client.get('/deploy/status')
        _print_json('Status (no instance configured)', resp.json())
        assert resp.json()['status'] == 'error'

        # With DEPLOY_INSTANCE_ID
        os.environ['DEPLOY_INSTANCE_ID'] = _local['instance_id']
        resp = client.get('/deploy/status')
        data = resp.json()
        _print_json('Status (instance configured)', data)

        assert data['status']      == 'running'
        assert data['instance_id'] == _local['instance_id']
        assert data['healthy']     is False   # No real server to health-check
        print(f'\n  healthy=False because no real FastAPI server is running on the twin IP.')
        print(f'  In production, this would hit https://{data["public_ip"]}/info/health')

        os.environ.pop('DEPLOY_INSTANCE_ID', None)

    # -----------------------------------------------------------------------
    # Step 5: Budget enforcement
    # -----------------------------------------------------------------------
    def test__05__budget_check(self):
        _print_section('Step 5: Budget enforcement (max 3 instances)')

        service = _local['service']

        # Create 2 more instances (total = 3, at limit)
        for i in range(2):
            result = service.create(
                instance_type = 't3.micro'             ,
                data_room_id  = f'room-{i + 2:03d}'    ,
                image_id      = 'ami-deploy-001'       ,
                admin         = 'qa-tester'            )
            print(f'  Created instance {i + 2}: {result["instance_id"]}')

        running = service.list_running()
        print(f'\n  Running count: {len(running)} (limit: 3)')

        # Try to create a 4th — should be rejected
        result = service.create(
            instance_type = 't3.micro'       ,
            data_room_id  = 'room-overflow'  ,
            image_id      = 'ami-deploy-001' ,
            admin         = 'qa-tester'      )

        _print_json('4th instance attempt (should fail)', result)
        assert result['status'] == 'error'
        assert 'limit' in result['message'].lower()
        print(f'\n  Budget enforcement working: rejected instance #4')

        # Also check budget cost estimate
        budget_status = service.get_budget_status()
        _print_json('Budget status', budget_status)
        print(f'\n  Hourly cost:  ${budget_status["hourly_total"]:.4f}')
        print(f'  Daily est:    ${budget_status["daily_estimate"]:.2f}')
        print(f'  Within budget: {budget_status["within_budget"]}')

    # -----------------------------------------------------------------------
    # Step 6: Stop and start an instance
    # -----------------------------------------------------------------------
    def test__06__stop_and_start(self):
        _print_section('Step 6: Stop and start an instance')

        service     = _local['service']
        instance_id = _local['instance_id']

        # Stop
        result = service.stop(instance_id=instance_id, admin='qa-tester')
        _print_json('Stop result', result)
        assert result['status'] == 'stopping'

        running = service.list_running()
        print(f'\n  Running after stop: {len(running)}')

        # Get details while stopped
        details = service.get_instance(instance_id=instance_id)
        _print_json('Instance details (stopped)', details)
        assert details['state'] == 'stopped'

        # Start
        result = service.start(instance_id=instance_id, admin='qa-tester')
        _print_json('Start result', result)
        assert result['status'] == 'starting'

        running = service.list_running()
        print(f'\n  Running after start: {len(running)}')

    # -----------------------------------------------------------------------
    # Step 7: Watchdog — skips healthy/recent instances
    # -----------------------------------------------------------------------
    def test__07__watchdog_skips_healthy(self):
        _print_section('Step 7: Watchdog skips recently-launched instances')

        fleet    = _local['fleet']
        provider = _local['provider']

        # Create a managed instance with tag
        managed = fleet.create_instance(
            image_id      = 'ami-deploy-001'              ,
            instance_type = 't3.micro'                    ,
            tags          = {'sg-deploy:managed': 'true'} )
        managed_id = managed['instance_id']
        print(f'  Created managed instance: {managed_id}')

        watchdog = Watchdog__Service(
            ec2_provider         = provider ,
            idle_timeout_minutes = 60       )  # 60 min timeout

        result = watchdog.check_and_stop_idle()
        _print_json('Watchdog result', result)

        print(f'\n  Checked {result["checked"]} managed instance(s)')
        print(f'  Actions taken: {len(result["actions"])}')
        assert len(result['actions']) == 0, 'Watchdog should skip recently-launched instances'
        print(f'  Watchdog correctly skipped the instance (within idle timeout)')

        # Cleanup managed instance
        fleet.terminate_instance(managed_id)

    # -----------------------------------------------------------------------
    # Step 8: Watchdog — stops idle instances
    # -----------------------------------------------------------------------
    def test__08__watchdog_stops_idle(self):
        _print_section('Step 8: Watchdog stops idle instances')

        fleet    = _local['fleet']
        provider = _local['provider']

        # Create a managed instance
        managed = fleet.create_instance(
            image_id      = 'ami-deploy-001'              ,
            instance_type = 't3.micro'                    ,
            tags          = {'sg-deploy:managed': 'true'} )
        managed_id = managed['instance_id']

        # Backdate the launch time to 2 hours ago
        twin = fleet.instances[managed_id]
        past = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        twin.state.launch_time = past
        print(f'  Created managed instance: {managed_id}')
        print(f'  Backdated launch_time to: {past}')

        watchdog = Watchdog__Service(
            ec2_provider         = provider ,
            idle_timeout_minutes = 30       )

        result = watchdog.check_and_stop_idle()
        _print_json('Watchdog result', result)

        assert len(result['actions']) == 1
        assert result['actions'][0]['instance_id'] == managed_id
        assert result['actions'][0]['action']      == 'stopped'
        print(f'\n  Watchdog correctly stopped idle instance {managed_id}')

    # -----------------------------------------------------------------------
    # Step 9: Terminate and check audit
    # -----------------------------------------------------------------------
    def test__09__terminate_and_audit(self):
        _print_section('Step 9: Terminate instance and check audit trail')

        service     = _local['service']
        instance_id = _local['instance_id']

        result = service.terminate(instance_id=instance_id, admin='qa-tester')
        _print_json('Terminate result', result)
        assert result['status'] == 'terminated'

        running = service.list_running()
        print(f'\n  Running after terminate: {len(running)}')

    # -----------------------------------------------------------------------
    # Step 10: Full audit trail inspection
    # -----------------------------------------------------------------------
    def test__10__full_audit_chain(self):
        _print_section('Step 10: Full audit trail')

        trail   = _local['trail']
        entries = trail.get_entries()

        print(f'  Total audit entries: {len(entries)}')
        print(f'  Chain valid:         {trail.verify_chain()}')

        for i, entry in enumerate(entries):
            print(f'\n  Entry {i + 1}:')
            print(f'    Action:    {entry.action}')
            print(f'    Admin:     {entry.admin}')
            print(f'    Timestamp: {entry.timestamp}')
            print(f'    Hash:      {entry.entry_hash[:16]}...')
            print(f'    Prev hash: {entry.prev_hash[:16] if entry.prev_hash else "(genesis)"}...')
            if entry.details:
                print(f'    Details:   {json.dumps(entry.details, default=str)}')

        assert trail.verify_chain() is True
        print(f'\n  Hash chain integrity verified.')


# ===========================================================================
# Part 2: AWS walkthrough (needs real credentials)
# ===========================================================================

def _has_aws_credentials():
    return (os.environ.get('AWS_ACCESS_KEY_ID', '') != '' and
            os.environ.get('AWS_SECRET_ACCESS_KEY', '') != '')


SKIP_AWS = 'AWS credentials not configured (need AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY)'

# Module-level state for AWS walkthrough
_aws = dict(instance_id='')


@pytest.mark.skipif(not _has_aws_credentials(), reason=SKIP_AWS)
class Test_QA__Deploy_Walkthrough__AWS(TestCase):

    # -----------------------------------------------------------------------
    # Step 1: Verify credentials work
    # -----------------------------------------------------------------------
    def test__1__verify_credentials(self):
        _print_section('Step 1: Verify AWS credentials')

        from sg_send_deploy.ec2.providers.EC2_Provider__AWS import EC2_Provider__AWS
        provider = EC2_Provider__AWS()

        # Just list instances — if credentials are bad this will throw
        instances = provider.list_instances()

        print(f'  Credentials:     valid')
        print(f'  Region:          {os.environ.get("AWS_DEFAULT_REGION", "not set")}')
        print(f'  Existing instances: {len(instances)}')

        for inst in instances:
            state = inst.get('state', {})
            state_name = state.get('Name', '') if isinstance(state, dict) else str(state)
            print(f'    {inst.get("instance_id", "?"):20s}  state={state_name:12s}  type={inst.get("instance_type", "?")}')

    # -----------------------------------------------------------------------
    # Step 2: List existing instances (detailed)
    # -----------------------------------------------------------------------
    def test__2__list_existing_instances(self):
        _print_section('Step 2: List existing instances (detailed)')

        service = Service__EC2_Instances()
        running = service.list_running()

        print(f'  Running/pending instances: {len(running)}')
        for inst in running:
            _print_json(f'Instance {inst["instance_id"]}', inst)

        budget = service.get_budget_status()
        _print_json('Current budget status', budget)

    # -----------------------------------------------------------------------
    # Step 3: Create a real instance
    # -----------------------------------------------------------------------
    def test__3__create_instance(self):
        _print_section('Step 3: Create a REAL EC2 instance')
        print(f'  WARNING: This creates a real EC2 instance (costs money)')
        print(f'  Instance will be t3.micro (cheapest)')

        service = Service__EC2_Instances()
        result  = service.create(
            instance_type = 't3.micro'                     ,
            data_room_id  = 'qa-walkthrough'               ,
            image_id      = os.environ.get('QA_AMI_ID', '') ,
            admin         = 'qa-tester'                    )

        _print_json('Create result', result)

        if result['status'] == 'created':
            _aws['instance_id'] = result['instance_id']
            print(f'\n  Instance created: {_aws["instance_id"]}')
            print(f'  Run test__4 to check status, test__5 to terminate')
        else:
            print(f'\n  Create failed: {result.get("message", "")}')
            print(f'  Set QA_AMI_ID env var to a valid AMI in your region')

    # -----------------------------------------------------------------------
    # Step 4: Check instance status
    # -----------------------------------------------------------------------
    def test__4__check_status(self):
        _print_section('Step 4: Check instance status')

        instance_id = _aws.get('instance_id', '') or os.environ.get('QA_INSTANCE_ID', '')
        if not instance_id:
            print(f'  No instance to check. Run test__3 first or set QA_INSTANCE_ID')
            return

        service = Service__EC2_Instances()
        details = service.get_instance(instance_id=instance_id)
        _print_json('Instance details', details)

        budget = service.get_budget_status()
        _print_json('Budget status', budget)

    # -----------------------------------------------------------------------
    # Step 5: Terminate instance (cleanup)
    # -----------------------------------------------------------------------
    def test__5__terminate_instance(self):
        _print_section('Step 5: Terminate instance (cleanup)')

        instance_id = _aws.get('instance_id', '') or os.environ.get('QA_INSTANCE_ID', '')
        if not instance_id:
            print(f'  No instance to terminate. Run test__3 first or set QA_INSTANCE_ID')
            return

        service = Service__EC2_Instances()
        result  = service.terminate(instance_id=instance_id, admin='qa-tester')
        _print_json('Terminate result', result)

        if result['status'] == 'terminated':
            print(f'\n  Instance {instance_id} terminated.')
            print(f'  Check your AWS console to confirm.')
        else:
            print(f'\n  Terminate failed: {result.get("message", "")}')

        # Show audit log
        log = service.get_audit_log()
        print(f'\n  Audit log ({len(log)} entries):')
        for entry in log:
            print(f'    {entry["action"]:25s}  admin={entry["admin"]:15s}  {entry["timestamp"]}')
