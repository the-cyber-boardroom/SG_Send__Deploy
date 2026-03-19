# ═══════════════════════════════════════════════════════════════════════════════
# Service__Chat__Sessions — session CRUD against Storage_FS
# ═══════════════════════════════════════════════════════════════════════════════

from memory_fs.storage_fs.Storage_FS                                           import Storage_FS
from memory_fs.storage_fs.providers.Storage_FS__Memory                         import Storage_FS__Memory
from osbot_utils.type_safe.Type_Safe                                           import Type_Safe
from osbot_utils.type_safe.primitives.domains.identifiers.safe_int.Timestamp_Now import Timestamp_Now
from osbot_utils.type_safe.type_safe_core.decorators.type_safe                 import type_safe
from osbot_utils.utils.Json                                                    import json_dumps
from sg_send_deploy_local_llm.schemas.types.Chat__Session_Id                   import Chat__Session_Id
from sg_send_deploy_local_llm.schemas.Schema__Chat__Session                    import Schema__Chat__Session

SESSIONS_FOLDER = 'sessions'

class Service__Chat__Sessions(Type_Safe):                                      # Session CRUD against Storage_FS
    storage_fs : Storage_FS = None                                             # pluggable backend

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.storage_fs is None:
            self.storage_fs = Storage_FS__Memory()

    def session_path(self, session_id):                                        # Storage path for a session
        return f'{SESSIONS_FOLDER}/{session_id}.json'

    @type_safe
    def create(self, session: Schema__Chat__Session) -> Schema__Chat__Session:
        data = json_dumps(session.json())
        self.storage_fs.file__save(self.session_path(session.id), data.encode())
        return session

    @type_safe
    def get(self, session_id: Chat__Session_Id) -> Schema__Chat__Session:
        raw = self.storage_fs.file__json(self.session_path(session_id))
        if not raw:
            return None
        return Schema__Chat__Session.from_json(raw)

    @type_safe
    def update(self, session: Schema__Chat__Session) -> Schema__Chat__Session:
        session.updated_at = Timestamp_Now()
        return self.create(session)

    @type_safe
    def delete(self, session_id: Chat__Session_Id) -> bool:
        path = self.session_path(session_id)
        if self.storage_fs.file__exists(path):
            self.storage_fs.file__delete(path)
            return True
        return False

    def list_sessions(self) -> list:                                           # Returns list of session summaries
        files = self.storage_fs.folder__files(f'{SESSIONS_FOLDER}/')
        sessions = []
        for filename in (files or []):
            path = f'{SESSIONS_FOLDER}/{filename}'
            raw  = self.storage_fs.file__json(path)
            if raw:
                session = Schema__Chat__Session.from_json(raw)
                sessions.append(dict(id            = str(session.id)         ,
                                     title         = str(session.title)      ,
                                     model         = str(session.model)      ,
                                     created_at    = int(session.created_at) ,
                                     message_count = len(session.messages)   ))
        return sorted(sessions, key=lambda s: s['created_at'], reverse=True)
