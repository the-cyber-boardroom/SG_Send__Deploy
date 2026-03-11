import os
import time

from sg_send_deploy.ec2.providers.EC2_Provider import EC2_Provider

class EC2_Provider__AWS(EC2_Provider):

    def run_instances(self, instance_type    : str  = 't3.micro' ,
                            image_id         : str  = ''         ,
                            key_name         : str  = ''         ,
                            security_group_id: str  = ''         ,
                            spot_instance    : bool = False       ,
                            tags             : dict = None        ) -> dict:
        from osbot_aws.aws.ec2.EC2 import EC2
        ec2    = EC2()
        kwargs = dict(image_id      = image_id      ,
                      instance_type = instance_type  )
        if key_name:
            kwargs['key_name'] = key_name
        if security_group_id:
            kwargs['security_group_id'] = security_group_id
        instance_id = ec2.instance_create(**kwargs)
        return dict(instance_id = instance_id or '',
                    public_ip   = ''               )

    def describe_instance(self, instance_id: str) -> dict:
        from osbot_aws.aws.ec2.EC2 import EC2
        ec2 = EC2()
        return ec2.instance_details(instance_id=instance_id)

    def list_instances(self) -> list:
        from osbot_aws.aws.ec2.EC2 import EC2
        ec2 = EC2()
        return ec2.instances_details()

    def terminate_instance(self, instance_id: str) -> dict:
        from osbot_aws.aws.ec2.EC2 import EC2
        ec2 = EC2()
        ec2.instance_terminate(instance_id=instance_id)
        return dict(status='terminated', instance_id=instance_id)

    def stop_instance(self, instance_id: str) -> dict:
        from osbot_aws.aws.ec2.EC2 import EC2
        ec2 = EC2()
        ec2.instance_stop(instance_id=instance_id)
        return dict(status='stopping', instance_id=instance_id)

    def start_instance(self, instance_id: str) -> dict:
        from osbot_aws.aws.ec2.EC2 import EC2
        ec2 = EC2()
        ec2.instance_start(instance_id=instance_id)
        return dict(status='starting', instance_id=instance_id)

    def key_pair_create(self, key_name: str, target_folder: str = '/tmp') -> dict:
        from osbot_aws.aws.ec2.EC2 import EC2
        ec2    = EC2()
        result = ec2.key_pair_create_to_file(key_name=key_name, target_folder=target_folder)
        return dict(key_pair_id = result.get('key_pair_id', ''),
                    key_name    = key_name                      ,
                    key_path    = result.get('path_key_pair', ''))

    def key_pair_delete(self, key_pair_id: str) -> dict:
        from osbot_aws.aws.ec2.EC2 import EC2
        ec2     = EC2()
        deleted = ec2.key_pair_delete(key_pair_id=key_pair_id)
        return dict(status='deleted' if deleted else 'failed', key_pair_id=key_pair_id)

    def key_pairs_list(self) -> list:
        from osbot_aws.aws.ec2.EC2 import EC2
        ec2       = EC2()
        key_pairs = ec2.key_pairs()
        return [dict(key_pair_id = kp.get('KeyPairId'  , ''),
                     key_name    = kp.get('KeyName'    , ''),
                     key_type    = kp.get('KeyType'    , ''),
                     created     = str(kp.get('CreateTime', '')))
                for kp in (key_pairs or [])]

    def security_group_create(self, group_name: str, description: str, vpc_id: str = '') -> dict:
        from osbot_aws.aws.ec2.EC2 import EC2
        ec2    = EC2()
        result = ec2.security_group_create(security_group_name = group_name  ,
                                           description         = description ,
                                           vpc_id              = vpc_id or None)
        data   = result.get('data', {})
        return dict(status            = result.get('status', 'ok'),
                    security_group_id = data.get('security_group_id', ''),
                    group_name        = group_name                       )

    def security_group_delete(self, group_id: str) -> dict:
        from osbot_aws.aws.ec2.EC2 import EC2
        ec2     = EC2()
        deleted = ec2.security_group_delete(security_group_id=group_id)
        return dict(status='deleted' if deleted else 'failed', group_id=group_id)

    def security_groups_list(self) -> list:
        from osbot_aws.aws.ec2.EC2 import EC2
        ec2    = EC2()
        groups = ec2.security_groups()
        return [dict(group_id    = sg.get('GroupId'     , ''),
                     group_name  = sg.get('GroupName'   , ''),
                     description = sg.get('Description' , ''),
                     vpc_id      = sg.get('VpcId'       , ''))
                for sg in (groups or [])]

    def security_group_authorize_ingress(self, group_id: str, port: int, cidr_ip: str) -> dict:
        from osbot_aws.aws.ec2.EC2 import EC2
        ec2 = EC2()
        return ec2.security_group_authorize_ingress(security_group_id = group_id ,
                                                    port              = port     ,
                                                    cidr_ip           = cidr_ip  )

    def security_group_revoke_ingress(self, group_id: str, port: int, cidr_ip: str) -> dict:
        from osbot_aws.aws.ec2.EC2 import EC2
        ec2    = EC2()
        result = ec2.client().revoke_security_group_ingress(
            GroupId       = group_id,
            IpPermissions = [dict(IpProtocol = 'tcp'                                ,
                                  FromPort   = port                                  ,
                                  ToPort     = port                                  ,
                                  IpRanges   = [dict(CidrIp=cidr_ip)]               )])
        return dict(status='revoked', group_id=group_id)

    def wait_for_instance_running(self, instance_id: str, timeout: int = 120) -> dict:
        from osbot_aws.aws.ec2.EC2 import EC2
        ec2       = EC2()
        deadline  = time.time() + timeout
        while time.time() < deadline:
            details = ec2.instance_details(instance_id=instance_id)
            state   = details.get('state', {}).get('Name', '')
            if state == 'running':
                return details
            time.sleep(2)
        raise TimeoutError(f'Instance {instance_id} did not reach running state within {timeout}s')
