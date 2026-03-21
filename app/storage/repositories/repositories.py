from sqlalchemy import select

from ..postgres.db_hellper import db_helper
from ..models.room import Room


class SQLAlchemyAuthRepository:
    async def create_room(self, room:Room)->Room:
        async with db_helper.transaction() as session:
            session.add(room)
            await session.flush()
            await session.refresh(room)
            return room