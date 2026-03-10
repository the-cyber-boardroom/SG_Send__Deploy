from unittest import TestCase

from sg_send_deploy.twins.aws.ec2.Type__Twin__EC2__Security_Group import Type__Twin__EC2__Security_Group


class Test__Type__Twin__EC2__Security_Group(TestCase):

    def test_create_security_group(self):
        twin = Type__Twin__EC2__Security_Group()
        result = twin.execute('create_security_group',
                              group_name  = 'sg-send-data-room' ,
                              description = 'SG/Send data room'  ,
                              vpc_id      = 'vpc-abc123'         )

        assert result['group_id'] != ''
        assert twin.config.group_name  == 'sg-send-data-room'
        assert twin.config.vpc_id      == 'vpc-abc123'

    def test_validate_posture__443_only_passes(self):
        twin = Type__Twin__EC2__Security_Group()
        twin.execute('create_security_group', group_name='sg-send')
        twin.execute('authorize_ingress', protocol='tcp', from_port=443, to_port=443)

        result = twin.execute('validate_posture')
        assert result['valid'] is True
        assert result['violations'] == []

    def test_validate_posture__non_443_fails(self):
        twin = Type__Twin__EC2__Security_Group()
        twin.execute('create_security_group', group_name='sg-bad')
        twin.execute('authorize_ingress', protocol='tcp', from_port=22, to_port=22)

        result = twin.execute('validate_posture')
        assert result['valid'] is False
        assert len(result['violations']) > 0
        assert 'non-443' in result['violations'][0]

    def test_validate_posture__egress_fails(self):
        twin = Type__Twin__EC2__Security_Group()
        twin.execute('create_security_group', group_name='sg-bad')
        twin.execute('authorize_ingress', protocol='tcp', from_port=443, to_port=443)
        twin.execute('authorize_egress', protocol='-1', cidr='0.0.0.0/0')

        result = twin.execute('validate_posture')
        assert result['valid'] is False
        assert any('Egress' in v for v in result['violations'])
