from osbot_fast_api_serverless.deploy.Deploy__Serverless__Fast_API  import Deploy__Serverless__Fast_API
from sg_send_deploy.lambda__deploy.deploy__config                   import (
    SG_SEND__DEPLOY__SERVICE_NAME        ,
    SG_SEND__DEPLOY__LAMBDA_DEPENDENCIES )
from sg_send_deploy.lambda__deploy.handler                          import run


class Deploy__Service(Deploy__Serverless__Fast_API):

    def deploy_lambda(self):
        with super().deploy_lambda() as _:
            try:
                import sg_send_deploy__ui__admin
                _.add_folder(sg_send_deploy__ui__admin.path)
            except ImportError:
                pass
            return _

    def handler(self):              return run
    def lambda_dependencies(self):  return SG_SEND__DEPLOY__LAMBDA_DEPENDENCIES
    def lambda_name(self):          return SG_SEND__DEPLOY__SERVICE_NAME
