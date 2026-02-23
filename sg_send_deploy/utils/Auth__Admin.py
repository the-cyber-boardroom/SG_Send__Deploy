import os
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name='X-API-Key', auto_error=False)


async def require_admin(api_key: str = Security(API_KEY_HEADER)):
    expected_key = os.environ.get('DEPLOY_ADMIN_API_KEY', '')
    if not expected_key:
        return dict(identity='dev-mode', authenticated=True)
    if api_key != expected_key:
        raise HTTPException(status_code=403, detail='Invalid admin API key')
    return dict(identity=api_key[:8] + '...', authenticated=True)
