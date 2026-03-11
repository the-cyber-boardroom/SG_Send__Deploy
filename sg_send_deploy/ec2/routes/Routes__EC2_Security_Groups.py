from osbot_fast_api.api.routes.Fast_API__Routes import Fast_API__Routes

from sg_send_deploy.ec2.actions.Service__EC2_Security_Groups import Service__EC2_Security_Groups

TAG__ROUTES_SECURITY_GROUPS = 'ec2-security-groups'

ROUTES_PATHS__SECURITY_GROUPS = [f'/{TAG__ROUTES_SECURITY_GROUPS}/security-groups'                  ,
                                 f'/{TAG__ROUTES_SECURITY_GROUPS}/security-groups/{{group_id}}'    ]


class Routes__EC2_Security_Groups(Fast_API__Routes):
    tag                     : str                          = TAG__ROUTES_SECURITY_GROUPS
    service_security_groups : Service__EC2_Security_Groups

    def security_groups(self) -> list:                                               # GET /ec2-security-groups/security-groups
        return self.service_security_groups.list_security_groups()

    def create_security_group(self, group_name  : str,                               # POST /ec2-security-groups/create-security-group
                                    description : str = '') -> dict:
        return self.service_security_groups.create_security_group(
            group_name  = group_name  ,
            description = description )

    def delete__group_id(self, group_id: str) -> dict:                               # DELETE /ec2-security-groups/delete/{group_id}
        return self.service_security_groups.delete_security_group(group_id=group_id)

    def authorize_ingress(self, group_id: str,                                       # POST /ec2-security-groups/authorize-ingress
                                port    : int,
                                cidr_ip : str = '0.0.0.0/0') -> dict:
        return self.service_security_groups.authorize_ingress(
            group_id = group_id ,
            port     = port     ,
            cidr_ip  = cidr_ip  )

    def revoke_ingress(self, group_id: str,                                          # POST /ec2-security-groups/revoke-ingress
                             port    : int,
                             cidr_ip : str = '0.0.0.0/0') -> dict:
        return self.service_security_groups.revoke_ingress(
            group_id = group_id ,
            port     = port     ,
            cidr_ip  = cidr_ip  )

    def setup_routes(self):
        self.add_route_get   (self.security_groups       )
        self.add_route_post  (self.create_security_group )
        self.add_route_delete(self.delete__group_id      )
        self.add_route_post  (self.authorize_ingress     )
        self.add_route_post  (self.revoke_ingress        )
        return self
