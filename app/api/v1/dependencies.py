from typing import Annotated
from fastapi import Depends, HTTPException, status
from app.api.schemas.auth import Auth
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from app.core.config import settings

oauth2_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
) -> Auth:
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    user_id = payload.get("user_id")
    role_token = payload.get("role")
    if user_id is None or role_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    return Auth(uuid=user_id, role=role_token)


async def check_admin_role(
    admin: Annotated[Auth, Depends(get_current_user)],
) -> Auth:
    if admin.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: admin access required",
        )
    return admin


async def check_user_role(
    user: Annotated[Auth, Depends(get_current_user)],
) -> Auth:
    if user.role != "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: user access required",
        )
    return user
