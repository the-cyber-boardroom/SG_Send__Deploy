# ═══════════════════════════════════════════════════════════════════════════════
# Routes__Sessions — session CRUD routes
# ═══════════════════════════════════════════════════════════════════════════════

from fastapi                                                                   import HTTPException
from osbot_fast_api.api.routes.Fast_API__Routes                                import Fast_API__Routes
from sg_send_deploy_local_llm.schemas.types.Chat__Session_Id                   import Chat__Session_Id
from sg_send_deploy_local_llm.service.Service__Chat__Sessions                  import Service__Chat__Sessions
from sg_send_deploy_local_llm.schemas.Schema__Chat__Session                    import Schema__Chat__Session
from sg_send_deploy_local_llm.schemas.Schema__Chat__Message                    import Schema__Chat__Message

class Routes__Sessions(Fast_API__Routes):                                      # Session CRUD
    tag             : str = 'api/sessions'
    session_service : Service__Chat__Sessions = None

    def sessions(self) -> list:                                                # GET /api/sessions/sessions — list all
        return self.session_service.list_sessions()

    def sessions__session_id(self, session_id: str) -> dict:                   # GET /api/sessions/sessions/{session_id}
        session = self.session_service.get(Chat__Session_Id(session_id))
        if session is None:
            raise HTTPException(status_code=404, detail='Session not found')
        return session.json()

    def create(self, model: str = 'gemma3:4b',                                # POST /api/sessions/create
                     title: str = ''         ,
                     messages: list = None   ) -> dict:
        session = Schema__Chat__Session(model=model, title=title)
        for msg_data in (messages or []):
            if isinstance(msg_data, dict):
                session.messages.append(Schema__Chat__Message(role    = msg_data.get('role', 'user'),
                                                              content = msg_data.get('content', '') ))
        if not str(session.title) and len(session.messages) > 0:               # auto-generate title
            first_content = str(session.messages[0].content)
            session.title = first_content[:50]
        result = self.session_service.create(session)
        return result.json()

    def update__session_id(self, session_id: str,                              # PUT /api/sessions/update/{session_id}
                                 model: str = ''  ,
                                 title: str = ''  ,
                                 messages: list = None) -> dict:
        existing = self.session_service.get(Chat__Session_Id(session_id))
        if existing is None:
            raise HTTPException(status_code=404, detail='Session not found')
        if model:
            existing.model = model
        if title:
            existing.title = title
        if messages is not None:
            from sg_send_deploy_local_llm.schemas.Schema__Chat__Message import List__Chat__Messages
            existing.messages = List__Chat__Messages()
            for msg_data in messages:
                if isinstance(msg_data, dict):
                    existing.messages.append(Schema__Chat__Message(role    = msg_data.get('role', 'user'),
                                                                   content = msg_data.get('content', '') ))
        result = self.session_service.update(existing)
        return result.json()

    def delete__session_id(self, session_id: str) -> dict:                     # DELETE /api/sessions/delete/{session_id}
        deleted = self.session_service.delete(Chat__Session_Id(session_id))
        if not deleted:
            raise HTTPException(status_code=404, detail='Session not found')
        return dict(deleted=True, session_id=session_id)

    def setup_routes(self):
        self.add_route_get   (self.sessions)
        self.add_route_get   (self.sessions__session_id)
        self.add_route_post  (self.create)
        self.add_route_put   (self.update__session_id)
        self.add_route_delete(self.delete__session_id)
        return self
