from enum import Enum
from osbot_utils.type_safe.primitives.domains.identifiers.safe_str.Safe_Str__Id import Safe_Str__Id


class EC2__Instance_Id      (Safe_Str__Id): pass
class EC2__AMI_Id           (Safe_Str__Id): pass
class EC2__Security_Group_Id(Safe_Str__Id): pass
class EC2__Key_Name         (Safe_Str__Id): pass
class EC2__VPC_Id           (Safe_Str__Id): pass
class EC2__Subnet_Id        (Safe_Str__Id): pass


class Enum__EC2__Instance_Type(str, Enum):
    T3_MICRO   = 't3.micro'
    T3_SMALL   = 't3.small'
    T3_MEDIUM  = 't3.medium'
    C7G_XLARGE = 'c7g.xlarge'

    def __str__(self): return self.value


class Enum__EC2__Instance_State(str, Enum):
    PENDING       = 'pending'
    RUNNING       = 'running'
    SHUTTING_DOWN = 'shutting-down'
    TERMINATED    = 'terminated'
    STOPPING      = 'stopping'
    STOPPED       = 'stopped'

    def __str__(self): return self.value
