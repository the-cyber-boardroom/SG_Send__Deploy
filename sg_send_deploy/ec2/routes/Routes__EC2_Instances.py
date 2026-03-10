from osbot_fast_api.api.routes.Fast_API__Routes import Fast_API__Routes

from sg_send_deploy.ec2.actions.Service__EC2_Instances import Service__EC2_Instances

TAG__ROUTES_EC2 = 'ec2'

ROUTES_PATHS__EC2 = [f'/{TAG__ROUTES_EC2}/instances'                       ,
                     f'/{TAG__ROUTES_EC2}/instances/{{instance_id}}'       ,
                     f'/{TAG__ROUTES_EC2}/instances/{{instance_id}}/start' ,
                     f'/{TAG__ROUTES_EC2}/instances/{{instance_id}}/stop'  ,
                     f'/{TAG__ROUTES_EC2}/audit-log'                       ,
                     f'/{TAG__ROUTES_EC2}/budget'                          ]


class Routes__EC2_Instances(Fast_API__Routes):
    tag               : str                    = TAG__ROUTES_EC2
    service_instances : Service__EC2_Instances

    def instances(self) -> list:                                              # GET /ec2/instances
        return self.service_instances.list_running()

    def instances__instance_id(self, instance_id: str) -> dict:               # GET /ec2/instances/{instance_id}
        return self.service_instances.get_instance(instance_id=instance_id)

    def create_instance(self, instance_type: str = 't3.micro',                # POST /ec2/instances
                              data_room_id : str = ''        ,
                              image_id     : str = ''        ,
                              key_name     : str = ''        ) -> dict:
        return self.service_instances.create(
            instance_type = instance_type ,
            data_room_id  = data_room_id  ,
            image_id      = image_id      ,
            key_name      = key_name      )

    def terminate__instance_id(self, instance_id: str) -> dict:               # DELETE /ec2/instances/{instance_id}
        return self.service_instances.terminate(instance_id=instance_id)

    def start__instance_id(self, instance_id: str) -> dict:                   # POST /ec2/instances/{instance_id}/start
        return self.service_instances.start(instance_id=instance_id)

    def stop__instance_id(self, instance_id: str) -> dict:                    # POST /ec2/instances/{instance_id}/stop
        return self.service_instances.stop(instance_id=instance_id)

    def audit_log(self) -> list:                                              # GET /ec2/audit-log
        return self.service_instances.get_audit_log()

    def budget(self) -> dict:                                                   # GET /ec2/budget
        return self.service_instances.get_budget_status()

    def setup_routes(self):
        self.add_route_get   (self.instances             )
        self.add_route_get   (self.instances__instance_id)
        self.add_route_post  (self.create_instance       )
        self.add_route_delete(self.terminate__instance_id)
        self.add_route_post  (self.start__instance_id    )
        self.add_route_post  (self.stop__instance_id     )
        self.add_route_get   (self.audit_log             )
        self.add_route_get   (self.budget                )
        return self
