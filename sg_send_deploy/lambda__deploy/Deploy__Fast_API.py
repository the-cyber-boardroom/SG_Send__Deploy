from osbot_fast_api_serverless.fast_api.routes.Routes__Info import Routes__Info
from osbot_fast_api_serverless.fast_api.Serverless__Fast_API import Serverless__Fast_API

from sg_send_deploy.ec2.actions.Service__EC2_Instances       import Service__EC2_Instances
from sg_send_deploy.ec2.actions.Service__EC2_Key_Pairs       import Service__EC2_Key_Pairs
from sg_send_deploy.ec2.actions.Service__EC2_Security_Groups import Service__EC2_Security_Groups
from sg_send_deploy.ec2.routes.Routes__EC2_Instances         import Routes__EC2_Instances
from sg_send_deploy.ec2.routes.Routes__EC2_Key_Pairs         import Routes__EC2_Key_Pairs
from sg_send_deploy.ec2.routes.Routes__EC2_Security_Groups   import Routes__EC2_Security_Groups
from sg_send_deploy.utils.Version                            import version__sg_send_deploy

DEPLOY__FAST_API__TITLE       = 'SG/Send Deploy Management API'
DEPLOY__FAST_API__DESCRIPTION = 'Infrastructure management for SGraph Send ephemeral data rooms'


class Deploy__Fast_API(Serverless__Fast_API):

    service_instances       : Service__EC2_Instances       = None
    service_key_pairs       : Service__EC2_Key_Pairs       = None
    service_security_groups : Service__EC2_Security_Groups = None

    def setup(self):
        with self.config as _:
            _.name        = DEPLOY__FAST_API__TITLE
            _.version     = version__sg_send_deploy
            _.description = DEPLOY__FAST_API__DESCRIPTION

        if self.service_instances is None:
            self.service_instances = Service__EC2_Instances()
        if self.service_key_pairs is None:
            self.service_key_pairs = Service__EC2_Key_Pairs()
        if self.service_security_groups is None:
            self.service_security_groups = Service__EC2_Security_Groups()

        return super().setup()

    def setup_routes(self):
        self.add_routes(Routes__Info)
        self.add_routes(Routes__EC2_Instances,
                        service_instances = self.service_instances)
        self.add_routes(Routes__EC2_Key_Pairs,
                        service_key_pairs = self.service_key_pairs)
        self.add_routes(Routes__EC2_Security_Groups,
                        service_security_groups = self.service_security_groups)
