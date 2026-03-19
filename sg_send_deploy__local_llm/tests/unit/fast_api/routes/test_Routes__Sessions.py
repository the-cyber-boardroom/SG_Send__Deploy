# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Routes__Sessions
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                              import TestCase
from tests.unit.Fast_API__Test_Objs__Local_LLM                             import setup__fast_api__local_llm__test_objs

class test_Routes__Sessions(TestCase):

    @classmethod
    def setUpClass(cls):
        test_objs  = setup__fast_api__local_llm__test_objs()
        cls.client = test_objs.fast_api__client

    def test__create_session(self):                                        # POST /api/sessions/create
        response = self.client.post('/api/sessions/create',
                                    json=dict(model    = 'gemma3:4b'    ,
                                              title    = 'Test session' ,
                                              messages = [dict(role='user', content='hello')]))
        assert response.status_code == 200
        data = response.json()
        assert 'id'    in data
        assert data['model'] == 'gemma3:4b'

    def test__list_sessions(self):                                         # GET /api/sessions/sessions
        self.client.post('/api/sessions/create',
                         json=dict(model='gemma3:4b', title='List test',
                                   messages=[dict(role='user', content='hi')]))
        response = self.client.get('/api/sessions/sessions')
        assert response.status_code == 200
        data = response.json()
        assert type(data) is list
        assert len(data)  >= 1

    def test__get_session(self):                                           # GET /api/sessions/sessions/{id}
        create = self.client.post('/api/sessions/create',
                                  json=dict(model='gemma3:4b', title='Get test',
                                            messages=[dict(role='user', content='test')])).json()
        sid      = create['id']
        response = self.client.get(f'/api/sessions/sessions/{sid}')
        assert response.status_code == 200
        assert response.json()['id'] == sid

    def test__get_session__not_found(self):                                # 404 for missing session
        response = self.client.get('/api/sessions/sessions/00000000')
        assert response.status_code == 404

    def test__delete_session(self):                                        # DELETE /api/sessions/delete/{id}
        create   = self.client.post('/api/sessions/create',
                                    json=dict(model='gemma3:4b', title='Delete test',
                                              messages=[dict(role='user', content='bye')])).json()
        sid      = create['id']
        response = self.client.delete(f'/api/sessions/delete/{sid}')
        assert response.status_code == 200
        assert response.json()['deleted'] is True
        assert self.client.get(f'/api/sessions/sessions/{sid}').status_code == 404
