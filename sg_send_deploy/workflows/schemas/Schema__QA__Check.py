from osbot_utils.type_safe.Type_Safe import Type_Safe


class Schema__QA__Check(Type_Safe):
    check_id        : str  = ''
    prompt          : str  = ''
    expected_schema : dict
