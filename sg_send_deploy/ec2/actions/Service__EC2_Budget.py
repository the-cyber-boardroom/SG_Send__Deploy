from sg_send_deploy.ec2.schemas.EC2_Budget_Config import EC2_Budget_Config
from sg_send_deploy.ec2.schemas.EC2_Budget_Config import INSTANCE_HOURLY_RATES


class Service__EC2_Budget:
    def __init__(self, config=None):
        self.config = config or EC2_Budget_Config()

    def check_instance_limit(self, current_count: int) -> dict:
        over_limit = current_count >= self.config.max_instances
        allowed    = True if not self.config.enforce_limits else not over_limit
        message    = ''
        if over_limit:
            message = f'Instance limit reached ({self.config.max_instances})'
            if not self.config.enforce_limits:
                message = f'Warning: {message} (not enforced)'
        return dict(
            allowed       = allowed                  ,
            current_count = current_count            ,
            max_instances = self.config.max_instances ,
            enforced      = self.config.enforce_limits,
            message       = message                  )

    def check_instance_type(self, instance_type: str) -> dict:
        allowed_types  = self.config.allowed_types()
        type_allowed   = instance_type in allowed_types
        allowed        = True if not self.config.enforce_limits else type_allowed
        message        = ''
        if not type_allowed:
            message = f'Instance type {instance_type} not allowed. Use: {allowed_types}'
            if not self.config.enforce_limits:
                message = f'Warning: {message} (not enforced)'
        return dict(
            allowed        = allowed         ,
            instance_type  = instance_type   ,
            allowed_types  = allowed_types   ,
            enforced       = self.config.enforce_limits,
            message        = message         )

    def check_can_create(self, current_count: int, instance_type: str = 't3.micro') -> dict:
        limit_check = self.check_instance_limit(current_count)
        if not limit_check['allowed']:
            return limit_check

        type_check = self.check_instance_type(instance_type)
        if not type_check['allowed']:
            return type_check

        return dict(allowed=True, message='', enforced=self.config.enforce_limits)

    def estimate_hourly_cost(self, instance_type: str) -> float:
        return INSTANCE_HOURLY_RATES.get(instance_type, 0.0)

    def estimate_daily_cost(self, running_instances: list) -> dict:
        hourly_total = 0.0
        breakdown    = []
        for instance in running_instances:
            itype  = instance.get('instance_type', 't3.micro')
            rate   = self.estimate_hourly_cost(itype)
            hourly_total += rate
            breakdown.append(dict(instance_id   = instance.get('instance_id', ''),
                                  instance_type = itype                           ,
                                  hourly_rate   = rate                            ))
        daily_total = hourly_total * 24
        return dict(
            hourly_total     = round(hourly_total, 4) ,
            daily_estimate   = round(daily_total , 2) ,
            daily_budget     = self.config.daily_budget_usd,
            within_budget    = daily_total <= self.config.daily_budget_usd,
            enforced         = self.config.enforce_limits,
            instance_count   = len(running_instances) ,
            breakdown        = breakdown              )
