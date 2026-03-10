from sg_send_deploy.twins.aws.ec2.schemas.Schema__Twin__EC2__Security_Group import Schema__Twin__Config__EC2__Security_Group
from sg_send_deploy.twins.aws.ec2.schemas.Schema__Twin__EC2__Security_Group import Schema__Twin__State__EC2__Security_Group
from sg_send_deploy.twins.aws.Type__Twin__AWS                               import Type__Twin__AWS

class Type__Twin__EC2__Security_Group(Type__Twin__AWS):
    config : Schema__Twin__Config__EC2__Security_Group
    state  : Schema__Twin__State__EC2__Security_Group

    def execute(self, action: str, **kwargs) -> dict:
        actions = dict(create_security_group    = self.action__create            ,
                       describe_security_groups = self.action__describe          ,
                       authorize_ingress        = self.action__authorize_ingress ,
                       authorize_egress         = self.action__authorize_egress  ,
                       validate_posture         = self.action__validate_posture  )

        handler = actions.get(action)
        if handler is None:
            return dict(status='error', message=f'Unknown action: {action}')
        return handler(**kwargs)

    def action__create(self, **kwargs) -> dict:
        self.config.group_id    = kwargs.get('group_id'   , self._generate_sg_id())
        self.config.group_name  = kwargs.get('group_name' , ''                    )
        self.config.description = kwargs.get('description', ''                    )
        self.config.vpc_id      = kwargs.get('vpc_id'     , ''                    )
        return dict(group_id = self.config.group_id)

    def action__describe(self, **kwargs) -> dict:
        return dict(group_id      = self.config.group_id      ,
                    group_name    = self.config.group_name     ,
                    description   = self.config.description    ,
                    vpc_id        = self.config.vpc_id         ,
                    ingress_rules = self.config.ingress_rules  ,
                    egress_rules  = self.config.egress_rules   ,
                    region        = self.config.region          )

    def action__authorize_ingress(self, **kwargs) -> dict:
        rule = dict(protocol  = kwargs.get('protocol' , 'tcp') ,
                    from_port = kwargs.get('from_port', 443  ) ,
                    to_port   = kwargs.get('to_port'  , 443  ) ,
                    cidr      = kwargs.get('cidr'     , '0.0.0.0/0'))
        self.config.ingress_rules.append(rule)
        return dict(status='ok', rule=rule)

    def action__authorize_egress(self, **kwargs) -> dict:
        rule = dict(protocol  = kwargs.get('protocol' , '-1') ,
                    from_port = kwargs.get('from_port', 0   ) ,
                    to_port   = kwargs.get('to_port'  , 0   ) ,
                    cidr      = kwargs.get('cidr'     , ''  ) )
        self.config.egress_rules.append(rule)
        return dict(status='ok', rule=rule)

    def action__validate_posture(self, **kwargs) -> dict:
        violations = []

        for rule in self.config.ingress_rules:
            if rule.get('from_port') != 443 or rule.get('to_port') != 443:
                violations.append(f'Ingress rule allows non-443 port: {rule}')

        if len(self.config.egress_rules) > 0:
            for rule in self.config.egress_rules:
                if rule.get('cidr') != '':
                    violations.append(f'Egress rule found (zero egress required): {rule}')

        return dict(valid      = len(violations) == 0 ,
                    violations = violations            )

    def _generate_sg_id(self) -> str:
        import hashlib
        seed = f'{self.config.group_name}-{self.config.vpc_id}'
        hash_val = hashlib.md5(seed.encode()).hexdigest()[:17]
        return f'sg-{hash_val}'
