# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Service__Chat__Sessions
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                              import TestCase
from sg_send_deploy_local_llm.schemas.Schema__Chat__Session                import Schema__Chat__Session
from sg_send_deploy_local_llm.schemas.Schema__Chat__Message                import Schema__Chat__Message
from sg_send_deploy_local_llm.schemas.types.Chat__Session_Id               import Chat__Session_Id
from sg_send_deploy_local_llm.service.Service__Chat__Sessions              import Service__Chat__Sessions

class test_Service__Chat__Sessions(TestCase):

    @classmethod
    def setUpClass(cls):                                                   # ONE TIME — in-memory storage
        cls.service = Service__Chat__Sessions()

    def create_test_session(self):                                         # Helper — create a session
        session = Schema__Chat__Session(model='gemma3:4b', title='Test')
        session.messages.append(Schema__Chat__Message(role='user', content='hello'))
        return self.service.create(session)

    def test__create_and_get(self):                                        # Create → get round-trip
        created = self.create_test_session()
        loaded  = self.service.get(created.id)
        assert loaded is not None
        assert str(loaded.id)    == str(created.id)
        assert str(loaded.title) == 'Test'
        assert len(loaded.messages) == 1

    def test__get__not_found(self):                                        # Get non-existent session
        result = self.service.get(Chat__Session_Id('00000000'))
        assert result is None

    def test__update(self):                                                # Update adds message
        created = self.create_test_session()
        created.messages.append(Schema__Chat__Message(role='assistant', content='hi'))
        self.service.update(created)
        loaded = self.service.get(created.id)
        assert len(loaded.messages) == 2

    def test__delete(self):                                                # Delete removes session
        created = self.create_test_session()
        assert self.service.delete(created.id) is True
        assert self.service.get(created.id)    is None

    def test__delete__not_found(self):                                     # Delete non-existent
        assert self.service.delete(Chat__Session_Id('00000000')) is False

    def test__list_sessions(self):                                         # List returns summaries
        self.create_test_session()
        sessions = self.service.list_sessions()
        assert type(sessions) is list
        assert len(sessions)  >= 1
        first = sessions[0]
        assert 'id'            in first
        assert 'title'         in first
        assert 'model'         in first
        assert 'message_count' in first
