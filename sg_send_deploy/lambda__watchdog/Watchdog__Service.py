import os
import ssl
import urllib.request
from datetime import datetime, timezone

from sg_send_deploy.ec2.providers.EC2_Provider import EC2_Provider


class Watchdog__Service:
    """EventBridge-triggered watchdog that stops idle EC2 deploy instances.

    Stateless: queries ec2:DescribeInstances each invocation.
    Identifies deploy instances by tag 'sg-deploy:managed=true'.
    Stops instances that fail the health check or exceed idle timeout."""

    def __init__(self, ec2_provider=None, idle_timeout_minutes=None):
        self.ec2_provider         = ec2_provider or self._default_provider()
        self.idle_timeout_minutes = idle_timeout_minutes or int(os.environ.get('WATCHDOG_IDLE_TIMEOUT_MINUTES', '30'))
        self.managed_tag_key      = 'sg-deploy:managed'
        self.managed_tag_value    = 'true'

    def _default_provider(self):
        from sg_send_deploy.ec2.providers.EC2_Provider__AWS import EC2_Provider__AWS
        return EC2_Provider__AWS()

    def check_and_stop_idle(self) -> dict:
        """Main watchdog logic. Returns summary of actions taken."""
        instances = self._list_managed_instances()
        actions   = []

        for instance in instances:
            instance_id = instance.get('instance_id', '')
            state       = instance.get('state', {})
            state_name  = state.get('Name', '') if isinstance(state, dict) else str(state)
            public_ip   = instance.get('public_ip', '')

            if state_name != 'running':
                continue

            healthy = self._health_check(public_ip) if public_ip else False

            if not healthy:
                launch_time = instance.get('launch_time', '')
                if launch_time and self._exceeds_idle_timeout(launch_time):
                    self.ec2_provider.stop_instance(instance_id=instance_id)
                    actions.append(dict(instance_id = instance_id ,
                                        action      = 'stopped'   ,
                                        reason      = 'unhealthy_and_idle'))

        return dict(checked   = len(instances) ,
                    actions   = actions         ,
                    timestamp = datetime.now(timezone.utc).isoformat())

    def _list_managed_instances(self) -> list:
        """List all instances tagged as managed by sg-deploy."""
        all_instances = self.ec2_provider.list_instances()
        managed       = []
        for instance in all_instances:
            tags = instance.get('tags', {})
            if isinstance(tags, dict) and tags.get(self.managed_tag_key) == self.managed_tag_value:
                managed.append(instance)
            elif isinstance(tags, list):
                for tag in tags:
                    if tag.get('Key') == self.managed_tag_key and tag.get('Value') == self.managed_tag_value:
                        managed.append(instance)
                        break
        return managed

    def _health_check(self, ip: str, timeout: int = 5) -> bool:
        """Check if the FastAPI server on the instance is responding."""
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode    = ssl.CERT_NONE
            url = f'https://{ip}/info/health'
            req = urllib.request.Request(url, method='GET')
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                return resp.status == 200
        except Exception:
            return False

    def _exceeds_idle_timeout(self, launch_time_str: str) -> bool:
        """Check if instance has been running longer than idle timeout."""
        try:
            if isinstance(launch_time_str, str):
                launch_time = datetime.fromisoformat(launch_time_str.replace('Z', '+00:00'))
            else:
                launch_time = launch_time_str

            now     = datetime.now(timezone.utc)
            elapsed = (now - launch_time).total_seconds() / 60.0
            return elapsed > self.idle_timeout_minutes
        except Exception:
            return True
