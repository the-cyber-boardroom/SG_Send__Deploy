# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Schema__Chat__Session
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                              import TestCase
from sg_send_deploy_local_llm.schemas.Schema__Chat__Session                import Schema__Chat__Session
from sg_send_deploy_local_llm.schemas.Schema__Chat__Message                import Schema__Chat__Message
from sg_send_deploy_local_llm.schemas.Schema__Chat__Message                import List__Chat__Messages
from sg_send_deploy_local_llm.schemas.types.Chat__Session_Id               import Chat__Session_Id

class test_Schema__Chat__Session(TestCase):

    def test__init__(self):                                                # Test auto-initialization
        with Schema__Chat__Session() as _:
            assert type(_.id)       is Chat__Session_Id
            assert len(str(_.id))   == 8
            assert type(_.messages) is List__Chat__Messages
            assert len(_.messages)  == 0

    def test__unique_ids(self):                                            # Each instance gets unique ID
        s1 = Schema__Chat__Session()
        s2 = Schema__Chat__Session()
        assert str(s1.id) != str(s2.id)

    def test__json_round_trip(self):                                       # Full serialization cycle
        session = Schema__Chat__Session(model='gemma3:4b', title='Test chat')
        session.messages.append(Schema__Chat__Message(role='user'     , content='hello'   ))
        session.messages.append(Schema__Chat__Message(role='assistant', content='hi there'))

        json_data = session.json()
        restored  = Schema__Chat__Session.from_json(json_data)

        assert str(restored.id)       == str(session.id)
        assert str(restored.model)    == 'gemma3:4b'
        assert len(restored.messages) == 2
        assert restored.messages[0].role == Enum__LLM__Role.USER

    def test__default_status(self):                                        # Default status is ACTIVE
        from sg_send_deploy_local_llm.schemas.types.Enum__Chat__Session_Status import Enum__Chat__Session_Status
        session = Schema__Chat__Session()
        assert session.status == Enum__Chat__Session_Status.ACTIVE


from sg_send_deploy_local_llm.schemas.types.Enum__LLM__Role import Enum__LLM__Role
