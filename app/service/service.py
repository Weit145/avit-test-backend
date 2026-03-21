import logging
from datetime import UTC, datetime, timedelta
from app.core.config import settings
from app.schemas.schemas_auth import JWT
from app.schemas.rooms import CreateRoom, OutRoom
from app.storage.repositories.repositories import SQLAlchemyAuthRepository
from app.utils.convert import convert_create_room_to_bd, convert_room_bd_to_out
import jwt

logger = logging.getLogger(__name__)

class Service:
    def __init__(self):
        self.repo = SQLAlchemyAuthRepository()
        pass
    
    def create_token(self,role:str)->JWT:
        expire = datetime.now(UTC) + timedelta(minutes=settings.time_jwt_minutes)
        to_encode = {
            "user_id": settings.admin_id if role == "admin" else settings.user_id,
            "role": role,
            "exp": expire,
        }
        encoded_jwt = jwt.encode(
            to_encode, settings.secret_key, algorithm=settings.algorithm
        )
        return JWT(jwt=encoded_jwt)
    
    async def create_room(self,room:CreateRoom)->OutRoom:
        room_bd = convert_create_room_to_bd(room)
        result = await self.repo.create_room(room_bd)
        return convert_room_bd_to_out(result)
    
service = Service()