from osbot_utils.type_safe.Type_Safe import Type_Safe


ALLOWED_INSTANCE_TYPES = ['t3.micro', 't3.small', 't3.medium']

INSTANCE_HOURLY_RATES  = { 't3.micro'  : 0.0104 ,
                           't3.small'  : 0.0209 ,
                           't3.medium' : 0.0418 }


class EC2_Budget_Config(Type_Safe):
    max_instances       : int   = 5
    daily_budget_usd    : float = 10.0
    idle_timeout_minutes: int   = 30
    max_instance_type   : str   = 't3.medium'
    enforce_limits      : bool  = True

    def allowed_types(self):
        return ALLOWED_INSTANCE_TYPES
