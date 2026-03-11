from sg_send_deploy.utils.Audit_Trail import Audit_Trail


class Service__EC2_Security_Groups:
    def __init__(self, audit_trail=None, ec2_provider=None):
        self.audit_trail  = audit_trail  or Audit_Trail()
        self.ec2_provider = ec2_provider or self._default_provider()

    def _default_provider(self):
        from sg_send_deploy.ec2.providers.EC2_Provider__AWS import EC2_Provider__AWS
        return EC2_Provider__AWS()

    def list_security_groups(self) -> list:
        try:
            return self.ec2_provider.security_groups_list()
        except Exception as e:
            return []

    def create_security_group(self, group_name: str, description: str, vpc_id: str = '', admin: str = '') -> dict:
        try:
            result = self.ec2_provider.security_group_create(
                group_name  = group_name  ,
                description = description ,
                vpc_id      = vpc_id      )

            self.audit_trail.record(
                action  = 'SECURITY_GROUP_CREATE'                              ,
                admin   = admin                                                ,
                details = dict(group_name        = group_name                  ,
                               security_group_id = result.get('security_group_id', '')))

            return result

        except Exception as e:
            return dict(status='error', message=str(e))

    def delete_security_group(self, group_id: str, admin: str = '') -> dict:
        try:
            result = self.ec2_provider.security_group_delete(group_id=group_id)

            self.audit_trail.record(
                action  = 'SECURITY_GROUP_DELETE'              ,
                admin   = admin                                ,
                details = dict(group_id = group_id             ))

            return result

        except Exception as e:
            return dict(status='error', message=str(e))

    def authorize_ingress(self, group_id: str, port: int, cidr_ip: str = '0.0.0.0/0', admin: str = '') -> dict:
        try:
            result = self.ec2_provider.security_group_authorize_ingress(
                group_id = group_id ,
                port     = port     ,
                cidr_ip  = cidr_ip  )

            self.audit_trail.record(
                action  = 'SECURITY_GROUP_AUTHORIZE_INGRESS'   ,
                admin   = admin                                ,
                details = dict(group_id = group_id             ,
                               port     = port                 ,
                               cidr_ip  = cidr_ip              ))

            return dict(status='authorized', group_id=group_id, port=port, cidr_ip=cidr_ip)

        except Exception as e:
            return dict(status='error', message=str(e))

    def revoke_ingress(self, group_id: str, port: int, cidr_ip: str = '0.0.0.0/0', admin: str = '') -> dict:
        try:
            result = self.ec2_provider.security_group_revoke_ingress(
                group_id = group_id ,
                port     = port     ,
                cidr_ip  = cidr_ip  )

            self.audit_trail.record(
                action  = 'SECURITY_GROUP_REVOKE_INGRESS'      ,
                admin   = admin                                ,
                details = dict(group_id = group_id             ,
                               port     = port                 ,
                               cidr_ip  = cidr_ip              ))

            return result

        except Exception as e:
            return dict(status='error', message=str(e))
