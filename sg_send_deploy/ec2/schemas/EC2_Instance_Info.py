from osbot_utils.type_safe.Type_Safe import Type_Safe


class EC2_Instance_Info(Type_Safe):
    instance_id    : str = ''
    status         : str = ''
    public_ip      : str = ''
    private_ip     : str = ''
    instance_type  : str = ''
    data_room_id   : str = ''
    launch_time    : str = ''
    uptime_seconds : int = 0
    ami_id         : str = ''
    key_name       : str = ''
