from osbot_fast_api.api.routes.Fast_API__Routes import Fast_API__Routes

from sg_send_deploy.workflows.actions.Operation__EC2__Ephemeral__LLM import Operation__EC2__Ephemeral__LLM

TAG__ROUTES_WORKFLOWS = 'workflows'

ROUTES_PATHS__WORKFLOWS = [f'/{TAG__ROUTES_WORKFLOWS}/execute']


class Routes__Workflows(Fast_API__Routes):
    tag       : str                             = TAG__ROUTES_WORKFLOWS
    operation : Operation__EC2__Ephemeral__LLM

    def execute(self, ami_id        : str  = ''            ,
                      instance_type : str  = 'c7g.xlarge'  ,
                      spot_instance : bool = True           ,
                      runner_ip     : str  = ''             ,
                      model         : str  = 'gemma3:4b'    ) -> dict:         # POST /workflows/execute
        return self.operation.execute(
            ami_id        = ami_id        ,
            instance_type = instance_type ,
            spot_instance = spot_instance ,
            runner_ip     = runner_ip     ,
            model         = model         )

    def setup_routes(self):
        self.add_route_post(self.execute)
        return self
