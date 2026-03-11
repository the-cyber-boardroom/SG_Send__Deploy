from sg_send_deploy.utils.Audit_Trail import Audit_Trail


class Service__EC2_Key_Pairs:
    def __init__(self, audit_trail=None, ec2_provider=None):
        self.audit_trail  = audit_trail  or Audit_Trail()
        self.ec2_provider = ec2_provider or self._default_provider()

    def _default_provider(self):
        from sg_send_deploy.ec2.providers.EC2_Provider__AWS import EC2_Provider__AWS
        return EC2_Provider__AWS()

    def list_key_pairs(self) -> list:
        try:
            return self.ec2_provider.key_pairs_list()
        except Exception as e:
            return []

    def create_key_pair(self, key_name: str, admin: str = '') -> dict:
        try:
            result = self.ec2_provider.key_pair_create(key_name=key_name)

            self.audit_trail.record(
                action  = 'KEY_PAIR_CREATE'                    ,
                admin   = admin                                ,
                details = dict(key_name    = key_name          ,
                               key_pair_id = result.get('key_pair_id', '')))

            return dict(status      = 'created'                        ,
                        key_pair_id = result.get('key_pair_id', '')     ,
                        key_name    = key_name                         ,
                        key_path    = result.get('key_path'   , '')    )

        except Exception as e:
            return dict(status='error', message=str(e))

    def delete_key_pair(self, key_pair_id: str, admin: str = '') -> dict:
        try:
            result = self.ec2_provider.key_pair_delete(key_pair_id=key_pair_id)

            self.audit_trail.record(
                action  = 'KEY_PAIR_DELETE'                    ,
                admin   = admin                                ,
                details = dict(key_pair_id = key_pair_id       ))

            return result

        except Exception as e:
            return dict(status='error', message=str(e))
