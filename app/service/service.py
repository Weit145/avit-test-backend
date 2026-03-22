from fastapi import HTTPException, status
import logging
import asyncio
import uuid
from typing import List
from datetime import UTC, datetime, timedelta
from app.core.config import settings
from app.schemas.schemas_auth import JWT
from app.schemas.rooms import CreateRoom, OutRoom
from app.schemas.schedule import CreateSchedule , OutSchedule
from app.storage.repositories.repositories import SQLAlchemyAuthRepository
from app.utils.convert import (
    convert_create_room_to_bd, 
    convert_room_bd_to_out, 
    convert_list_bd_to_out, 
    convert_create_schedule_to_bd,
    convert_schedule_bd_to_out
)

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

    async def read_rooms(self)->List[OutRoom]:
        result = await self.repo.read_rooms()
        return convert_list_bd_to_out(result)
    
    async def create_schedule(
        self,
        roomId:uuid.UUID, 
        schedule: CreateSchedule
    )->OutSchedule:
        room_task = asyncio.create_task(self.repo.read_room(roomId))
        schedule_task = asyncio.create_task(self.repo.read_schedule(roomId))
        room, existing_schedule = await asyncio.gather(room_task, schedule_task)
        if room is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Room not found",
            )
        if existing_schedule is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Schedule already create",
            )
        schedule_bd = convert_create_schedule_to_bd(schedule,roomId)
        result = await self.repo.create_schedule(schedule_bd)
        return convert_schedule_bd_to_out(result)

service = Service()