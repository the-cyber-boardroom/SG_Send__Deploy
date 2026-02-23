from osbot_fast_api_serverless.fast_api.routes.Routes__Info import Routes__Info
from osbot_fast_api_serverless.fast_api.Serverless__Fast_API import Serverless__Fast_API

from sg_send_deploy.ec2.actions.Service__EC2_Instances import Service__EC2_Instances
from sg_send_deploy.ec2.routes.Routes__EC2_Instances   import Routes__EC2_Instances
from sg_send_deploy.utils.Version                      import version__sg_send_deploy

DEPLOY__FAST_API__TITLE       = 'SG/Send Deploy Management API'
DEPLOY__FAST_API__DESCRIPTION = 'Infrastructure management for SGraph Send ephemeral data rooms'


class Deploy__Fast_API(Serverless__Fast_API):

    service_instances : Service__EC2_Instances = None

    def setup(self):
        with self.config as _:
            _.name        = DEPLOY__FAST_API__TITLE
            _.version     = version__sg_send_deploy
            _.description = DEPLOY__FAST_API__DESCRIPTION

        if self.service_instances is None:
            self.service_instances = Service__EC2_Instances()

        return super().setup()

    def setup_routes(self):
        self.add_routes(Routes__Info)
        self.add_routes(Routes__EC2_Instances,
                        service_instances = self.service_instances)
