from collections.abc import Callable

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from starlette.status import HTTP_403_FORBIDDEN

from backend.auth.security import verify_bearer_token
from backend.config import get_settings
from backend.models.database import UserRecord, get_session

ROLE_ANALYST = "analyst"
ROLE_SUPERVISOR = "supervisor"
ROLE_AUDITOR = "auditor"
ROLE_ADMIN = "admin"
session_dependency = Depends(get_session)


def seed_default_users(session: Session) -> None:
    from backend.auth.security import hash_password

    defaults = [
        ("analyst", "analyst123", [ROLE_ANALYST]),
        ("supervisor", "supervisor123", [ROLE_ANALYST, ROLE_SUPERVISOR]),
        ("auditor", "auditor123", [ROLE_AUDITOR]),
        ("admin", "admin123", [ROLE_ANALYST, ROLE_SUPERVISOR, ROLE_AUDITOR, ROLE_ADMIN]),
    ]
    for username, password, roles in defaults:
        if session.get(UserRecord, username) is None:
            session.add(UserRecord(username=username, password_hash=hash_password(password), roles=roles))
    session.commit()


def current_identity(request: Request, session: Session = session_dependency) -> dict:
    settings = get_settings()
    payload = verify_bearer_token(request.headers.get("Authorization"))
    if payload is None:
        if settings.enable_api_key_auth:
            raise HTTPException(status_code=401, detail="Missing or invalid bearer token")
        return {"sub": "demo", "roles": [ROLE_ADMIN, ROLE_SUPERVISOR, ROLE_ANALYST, ROLE_AUDITOR]}

    username = str(payload["sub"])
    user = session.get(UserRecord, username)
    if user is not None and not user.is_active:
        raise HTTPException(status_code=401, detail="User disabled")
    roles = list(user.roles if user is not None else payload.get("roles") or [ROLE_ANALYST])
    return {"sub": username, "roles": roles}


def require_roles(*allowed_roles: str) -> Callable:
    identity_dependency = Depends(current_identity)

    def dependency(identity: dict = identity_dependency) -> dict:
        roles = set(identity.get("roles") or [])
        if ROLE_ADMIN not in roles and roles.isdisjoint(allowed_roles):
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Insufficient role")
        return identity

    return dependency
