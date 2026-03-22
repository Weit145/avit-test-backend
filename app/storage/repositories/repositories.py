from sqlalchemy import select
import uuid
from typing import List
from ..postgres.db_hellper import db_helper
from ..models import Room, Schedule


class SQLAlchemyAuthRepository:
    async def create_room(self, room:Room)->Room:
        async with db_helper.transaction() as session:
            session.add(room)
            await session.flush()
            await session.refresh(room)
            return room
    
    async def read_rooms(self)->List[Room]:
        async with db_helper.session_factory() as session:
            stmt = select(Room)
            result = await session.execute(stmt)
            return result.scalars().all()
    
    async def read_room(self, roomId: uuid.UUID)->Room|None:
        async with db_helper.session_factory() as session:
            stmt = select(Room).where(Room.id==roomId)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
    
    async def read_schedule(self, roomId: uuid.UUID)->Schedule|None:
        async with db_helper.session_factory() as session:
            stmt = select(Schedule).where(Schedule.room_id==roomId)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
    
    async def create_schedule(self, schedule:Schedule)->Schedule:
        async with db_helper.transaction() as session:
            session.add(schedule)
            await session.flush()
            await session.refresh(schedule)
            return schedule