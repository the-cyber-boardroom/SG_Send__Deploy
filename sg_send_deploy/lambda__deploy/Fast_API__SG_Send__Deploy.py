from osbot_fast_api.api.routes.Routes__Set_Cookie               import Routes__Set_Cookie
from osbot_fast_api_serverless.fast_api.Serverless__Fast_API    import Serverless__Fast_API
from osbot_fast_api_serverless.fast_api.routes.Routes__Info     import Routes__Info

from sg_send_deploy.ec2.actions.Service__EC2_Instances               import Service__EC2_Instances
from sg_send_deploy.ec2.routes.Routes__EC2_Instances                 import Routes__EC2_Instances
from sg_send_deploy.workflows.actions.Operation__EC2__Ephemeral__LLM import Operation__EC2__Ephemeral__LLM
from sg_send_deploy.workflows.routes.Routes__Workflows               import Routes__Workflows
from sg_send_deploy.utils.Version                                    import version__sg_send_deploy
from sg_send_deploy.lambda__deploy.deploy__config                    import (
    SG_SEND__DEPLOY__FAST_API__TITLE ,
    SG_SEND__DEPLOY__FAST_API__DESC  )


class Fast_API__SG_Send__Deploy(Serverless__Fast_API):

    service_instances : Service__EC2_Instances        = None
    llm_operation     : Operation__EC2__Ephemeral__LLM = None

    def setup(self):
        with self.config as _:
            _.name        = SG_SEND__DEPLOY__FAST_API__TITLE
            _.version     = version__sg_send_deploy
            _.description = SG_SEND__DEPLOY__FAST_API__DESC

        if self.service_instances is None:
            self.service_instances = Service__EC2_Instances()

        if self.llm_operation is None:
            self.llm_operation = Operation__EC2__Ephemeral__LLM(
                ec2_provider = self.service_instances.ec2_provider,
                audit_trail  = self.service_instances.audit_trail )

        return super().setup()

    def setup_routes(self):
        self.setup_static_routes()
        self.add_routes(Routes__Info                                          )
        self.add_routes(Routes__Set_Cookie                                    )
        self.add_routes(Routes__EC2_Instances,
                        service_instances = self.service_instances            )
        self.add_routes(Routes__Workflows,
                        operation = self.llm_operation                        )

    def setup_static_routes(self):
        try:
            import sg_send_deploy__ui__admin
            from osbot_fast_api.api.decorators.route_path import route_path
            from starlette.responses                      import RedirectResponse
            from starlette.staticfiles                    import StaticFiles
            from sg_send_deploy.lambda__deploy.deploy__config import (
                UI__ADMIN__ROUTE__PATH__CONSOLE ,
                UI__ADMIN__MAJOR__VERSION       ,
                UI__ADMIN__LATEST__VERSION      ,
                UI__ADMIN__START_PAGE           )

            path_static_folder  = sg_send_deploy__ui__admin.path
            path_static         = f'/{UI__ADMIN__ROUTE__PATH__CONSOLE}'
            path_latest_version = (f'/{UI__ADMIN__ROUTE__PATH__CONSOLE}'
                                   f'/{UI__ADMIN__MAJOR__VERSION}'
                                   f'/{UI__ADMIN__LATEST__VERSION}'
                                   f'/{UI__ADMIN__START_PAGE}.html')

            self.app().mount(path_static,
                             StaticFiles(directory=path_static_folder),
                             name=UI__ADMIN__ROUTE__PATH__CONSOLE)

            @route_path(path=f'/{UI__ADMIN__ROUTE__PATH__CONSOLE}')
            def redirect_to_latest():
                return RedirectResponse(url=path_latest_version)

            self.add_route_get(redirect_to_latest)
        except ImportError:
            pass
