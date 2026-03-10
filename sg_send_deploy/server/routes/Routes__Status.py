import os
import urllib.request
import ssl

from osbot_fast_api.api.routes.Fast_API__Routes import Fast_API__Routes

from sg_send_deploy.ec2.providers.EC2_Provider import EC2_Provider

TAG__ROUTES_DEPLOY = 'deploy'

ROUTES_PATHS__DEPLOY = [f'/{TAG__ROUTES_DEPLOY}/status']


class Routes__Status(Fast_API__Routes):
    tag          : str          = TAG__ROUTES_DEPLOY
    ec2_provider : EC2_Provider

    def status(self) -> dict:                                                   # GET /deploy/status
        """Stateless status check. Queries EC2 DescribeInstances fresh each call.

        Returns the state of the deploy instance and whether it is healthy."""
        instance_id = os.environ.get('DEPLOY_INSTANCE_ID', '')
        if not instance_id:
            return dict(status  = 'error',
                        message = 'DEPLOY_INSTANCE_ID not configured')

        try:
            details = self.ec2_provider.describe_instance(instance_id=instance_id)
        except Exception as e:
            return dict(status  = 'error',
                        message = f'ec2:DescribeInstances failed: {e}')

        state = details.get('state', {})
        if isinstance(state, dict):
            state_name = state.get('Name', '')
        else:
            state_name = str(state)

        public_ip = details.get('public_ip', '')

        result = dict(status      = state_name   ,
                      instance_id = instance_id   ,
                      public_ip   = public_ip     ,
                      healthy     = False          )

        if state_name == 'running' and public_ip:
            result['healthy']  = self._health_check(public_ip)
            if result['healthy']:
                result['endpoint'] = f'https://{public_ip}'

        return result

    def _health_check(self, ip: str, timeout: int = 5) -> bool:
        """Ping the FastAPI health endpoint on the EC2 instance."""
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

    def setup_routes(self):
        self.add_route_get(self.status)
        return self
