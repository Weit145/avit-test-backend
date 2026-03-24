from datetime import datetime, timedelta, UTC
import jwt
from app.core.config import settings


class JWTService:
    def create_token(self, user_id: str, role: str) -> str:
        expire = datetime.now(UTC) + timedelta(minutes=settings.time_jwt_minutes)
        to_encode = {
            "user_id": user_id,
            "role": role,
            "exp": expire,
        }
        encoded_jwt = jwt.encode(
            to_encode, settings.secret_key, algorithm=settings.algorithm
        )
        return encoded_jwt

    def decode_token(self, token: str) -> dict:
        return jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
