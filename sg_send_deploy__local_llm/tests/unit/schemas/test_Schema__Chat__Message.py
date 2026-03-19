# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Schema__Chat__Message and List__Chat__Messages
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                              import TestCase
from sg_send_deploy_local_llm.schemas.Schema__Chat__Message                import Schema__Chat__Message
from sg_send_deploy_local_llm.schemas.Schema__Chat__Message                import List__Chat__Messages
from sg_send_deploy_local_llm.schemas.types.Enum__LLM__Role               import Enum__LLM__Role

class test_Schema__Chat__Message(TestCase):

    def test__init__(self):                                                # Test auto-initialization
        with Schema__Chat__Message() as _:
            assert type(_)         is Schema__Chat__Message
            assert _.role          is None                                 # Enum defaults to None

    def test__with_values(self):                                           # Test construction with values
        msg = Schema__Chat__Message(role='user', content='hello')
        assert msg.role == Enum__LLM__Role.USER
        assert 'hello' in str(msg.content)

    def test__invalid_role(self):                                          # Test enum validation
        with self.assertRaises((ValueError, Exception)):
            Schema__Chat__Message(role='invalid')

    def test__json_round_trip(self):                                       # Test serialization
        msg       = Schema__Chat__Message(role='user', content='test')
        json_data = msg.json()
        restored  = Schema__Chat__Message.from_json(json_data)
        assert restored.role == Enum__LLM__Role.USER
        assert 'test' in str(restored.content)

    def test__list_collection(self):                                       # Test typed list
        messages = List__Chat__Messages()
        messages.append(Schema__Chat__Message(role='user', content='hi'))
        assert len(messages)     == 1
        assert type(messages)    is List__Chat__Messages
        assert type(messages[0]) is Schema__Chat__Message
